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

# The directory on your machine, where to copy the data from.
SRC_DIR=/home/ubuntu/workspace/moodlenet
# The installation directory where the software is installed on the remote server.
INSTALL_DIR=moodlenet-dev
# Directory that contains the simple-file-store directories and the config files
# (on the remote server)
RESOURCE_DIR=moodlenet-simple-file-store
# The remote server and username, as it can be used by ssh/rsync.
REMOTE_HOST=mymnet-server
# The domain name (and path) where your MoodleNet installation can be reached via the web.
MNET_DOMAIN=https://moodlenet.example.org
# How many releases to keep.
RELEASES_TO_KEEP=5

# Determine the current release number and increase it by one. The
# release number is stored in the file release.version on the remote server.
release_number=$(ssh $REMOTE_HOST 'cat release.version')
if [ $? -ne 0 ]; then
    release_number=0
fi
release_number=$((release_number+1))
ssh $REMOTE_HOST "echo $release_number > release.version"

# Build the new release directory.
release_dir=moodlenet-release-${release_number}

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


echo 'done'
echo 'Change symlink and restart service ...'

# Stop the service, change the symlink and restart it
ssh ${REMOTE_HOST} "killall 'npm run dev-start-backend my-dev' && \
    rm ${INSTALL_DIR} && ln -s ${release_dir} ${INSTALL_DIR} && \
    cd ${INSTALL_DIR} && nohup npm run dev-start-backend my-dev &"
# Copy the lastest webapp built at the appropriate place
ssh $REMOTE_HOST "cp -r ${release_dir}/react-app_latest-build/* \
    ${release_dir}/.dev-machines/my-dev/fs/@moodlenet/react-app/webapp-build/latest-build/."

echo 'done'
echo -n "Try to reach ${MNET_DOMAIN} ... "
# Try to reach the site:
retries=5
while [ $retries -gt 0 ]; do
    http_code=$(curl -o /dev/null -s -w "%{http_code}\n" ${MNET_DOMAIN})
    if [ $http_code -lt 300 ]; then
        echo "OK with response $http_code"
        retries=0
    else
        sleep 2
        retries=$((retries-1))
        echo "failed with response $http_code"
        if [ $retries -gt 0 ]; then
           echo -n 'Retry ... '
        fi
    fi 
done

echo -n 'Remove older release ... '
# Remove older releases (here just go x version numbers back).
old_release_dir=$((release_number-RELEASES_TO_KEEP))
ssh $REMOTE_HOST "rm -r moodlenet-release-${old_release_dir}"
echo 'done'