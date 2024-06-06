#!/bin/bash

# Deploy your moodlenet dev environment to a public machine. On the public server
# it is assumed, that you:
# - you have an installation directory that is referred in the configs of MoodleNet
# - you have a resources directory that contains:
#   - a config directory with the current config files and crypto keys.
#   - that contains the four directories that have the simple-file-store mechanism where
#     all the uploaded files are stored.
# - use systemd start/stop scripts for MoodleNet (see this repo)
# - the "machine name" where the MoodleNet dev install is running is named: my-dev.
#
# The script copies all files from your dev machine to the server into a new created
# release directory. Then all adjustments (copy config files, symlink simple-file-stores)
# are done for the release dir. Finally the official MoodleNet install directory is
# symlinked to that release dir and the service is restarted.
# All variables in capitalized letters should be adjusted to your setup.

# Fetch deploy config
if [ -z $1 ] || [ ! -e $1 ]; then
    echo 'No or inexistend deployment config file given'
    exit 1;
fi

source $1

# Check config $SRC_DIR
if [ -z $SRC_DIR ] || [ ! -d $SRC_DIR ]; then
    echo "Missing parameter \$SRC_DIR or inexistent dir $SRC_DIR"
    exit 1
fi

# Check all other config variables.
if [[ -z $INSTALL_DIR  || -z $RESOURCE_DIR || -z $REMOTE_HOST || -z $MNET_DOMAIN ]]; then
    echo 'Missing config: $INSTALL_DIR or $RESOURCE_DIR or $REMOTE_HOST or $MNET_DOMAIN'
    exit 1
fi

# How many releases to keep.
if [ -z $RELEASES_TO_KEEP ]; then
    RELEASES_TO_KEEP=5
fi
# Zip old releases
if [ -z $ZIP_OLD ]; then
    ZIP_OLD=1
fi

# Prefix for the release directories
release_dir_prefix='moodlenet-release-'
# Determine the current release number and increase it by one. The
# release number is stored in the file release.version on the remote server.
release_number=$(ssh $REMOTE_HOST 'cat release.version')
if [ $? -ne 0 ]; then
    release_number=0
fi
release_number=$((release_number+1))
ssh $REMOTE_HOST "echo $release_number > release.version"

# Build the new release directory.
release_dir=${release_dir_prefix}${release_number}
if [ ${release_dir:0:1} != '/' ]; then
    homedir=$(ssh $REMOTE_HOST pwd)
    release_dir=$homedir/$release_dir
fi

echo "Create new release in ${release_dir_prefix}${release_number}"

# Determine absolute path of the resouce dir when not already given.
# Absolute dir is required for symlinks.
if [ ${RESOURCE_DIR:0:1} != '/' ]; then
    homedir=$(ssh $REMOTE_HOST pwd)
    RESOURCE_DIR=$homedir/$RESOURCE_DIR
fi

echo -n "Copy the files to the remote server ... "

# Copy the code into the new release dir.
rsync -az ${SRC_DIR}/ \
   ${REMOTE_HOST}:${release_dir} \
   --exclude 'ed-resource/simple-file-store' \
   --exclude 'collection/simple-file-store' \
   --exclude 'organization/simple-file-store' \
   --exclude 'web-user/simple-file-store' \
   --exclude '.dev-machines/my-dev/log' \
   --exclude '.git' \
   --exclude '.gitignore' \
   --exclude '.husky' \
   --exclude '.idea' \
   --exclude '.vscode' \
   --exclude 'default.c*'

# Copy the built webapp into the new release dir
rsync -az ${SRC_DIR}/.dev-machines/my-dev/fs/@moodlenet/react-app/webapp-build/latest-build/ ${REMOTE_HOST}:${release_dir}/react-app_latest-build

echo 'done'
echo -n 'Copy config and link resources ... '

# Adjust symlinks for simple-file-store and copy config files to release dir
ssh $REMOTE_HOST "cp ${RESOURCE_DIR}/config/* ${release_dir}/.dev-machines/my-dev/."
for i in collection ed-resource organization web-user; do
    ssh $REMOTE_HOST "ln -s ${RESOURCE_DIR}/${i}/simple-file-store ${release_dir}/.dev-machines/my-dev/fs/@moodlenet/${i}"
done
# crypto keys must also be right unter .dev-machines
ssh $REMOTE_HOST "cp ${release_dir}/.dev-machines/my-dev/*crypto* ${release_dir}/.dev-machines"

# Fix paths in package.json and other location from old dev location to installed location
ssh $REMOTE_HOST "cd ${release_dir}; grep -lri $SRC_DIR * | while read f ; do sed -i 's|${SRC_DIR}|${release_dir}|g' \$f; done"
ssh $REMOTE_HOST "cd ${release_dir}/.dev-machines; grep -lri $SRC_DIR * | while read f ; do sed -i 's|${SRC_DIR}|${release_dir}|g' \$f; done"


echo 'done'
echo 'Change symlink and restart service ...'

# Stop the service, change the symlink and restart it
ssh ${REMOTE_HOST} "killall node && \
    rm ${INSTALL_DIR} && ln -s ${release_dir} ${INSTALL_DIR}"
ssh ${REMOTE_HOST} "cd ${INSTALL_DIR} ; nohup npm run dev-start-backend my-dev > ~/nohup.out.${release_number} 2>&1 &" &
if [ $? -ne 0 ]; then
    echo 'failed'
else
    echo 'done'
fi

echo -n "Try to reach ${MNET_DOMAIN} ... "
# Try to reach the site:
retries=10
while [ $retries -gt 0 ]; do
    http_code=$(curl -o /dev/null -s -w "%{http_code}\n" ${MNET_DOMAIN})
    if [ $http_code -lt 300 ]; then
        echo "OK with response $http_code"
        retries=0
    else
        sleep 5
        retries=$((retries-1))
        echo "failed with response $http_code"
        if [ $retries -gt 0 ]; then
           echo -n 'Retry ... '
        fi
    fi 
done

# Remove older releases (here just go back x version numbers).
old_release_dir=$((release_number-RELEASES_TO_KEEP))
echo -n "Remove older release: ${release_dir_prefix}${old_release_dir} ... "
ssh $REMOTE_HOST "if [ -d ${release_dir_prefix}${old_release_dir} ]; \
    then \
        echo 'remove old dir'; rm -r ${release_dir_prefix}${old_release_dir}; \
    fi"
ssh $REMOTE_HOST "if [ -e ${release_dir_prefix}${old_release_dir}.tar.gz ]; \
    then \
        echo 'remove old tar'; rm ${release_dir_prefix}${old_release_dir}.tar.gz; \
    fi"

# Zip two previous releases
if [ $ZIP_OLD -eq 1 ]; then
    twoback=$((release_number-2))
    echo -n "Zip release: ${release_dir_prefix}${twoback} ... "
    ssh $REMOTE_HOST "if [ -d ${release_dir_prefix}${twoback} ]; \
        then \
            tar -czf ${release_dir_prefix}${twoback}.tar.gz ${release_dir_prefix}${twoback}; \
            rm -r ${release_dir_prefix}${twoback}; \
        fi"
   echo 'done'
   ssh $REMOTE_HOST "if [ -e ~/nohup.out.${twoback} ]; then rm ~/nohup.out.${twoback}; fi"
fi
