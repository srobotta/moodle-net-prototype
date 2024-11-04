# Tweaks running MoodleNet

## Arango DB

### Webadmin

To access the Agango DB browser backend, simply navigate in your browser to
http://localhost:8529/

This also works if the server is remote. In this case I use ssh portforwarding
in this way `ssh -NL 8529:localhost:8529 user@moodlenet.server`.

### Authentication

Be aware that by default, the docker container for Arango has **authentication disabled**. You
notice that when accessing the webinterface or using MoodleNet, no credentials are provided and
used.

After running the arangodb for the first time, login to the database via the webfrontend, in the left navigation menu and:
1. go to Users
1. click on "Add user"
1. provide a user name and a password and click "Create"
1. in the list of users, click on the new user name to edit the user
1. in the tabs on top, click the "Permissions" tab
1. for all "moodlenet__*" tables, set the permission to "administrate"

After having the new user, the MoodleNet config file needs to be adapted e.g.
`moodlenet/.dev-machines/my-dev/default.config.json` and the database section needs to have the
new credentials:

```
"@moodlenet/arangodb": {
    "connectionCfg": {
        "url": "http://localhost:8529",
        "auth": {
            "username": "moodlenetuser",
            "password": "theNewPassword"
        }
    }
}
```

You may also deactivate the root user in the Arango DB user list, or set him a strong password.

In the `docker-composer.yml` delete the line `ARANGO_NO_AUTH: '1'` at the arangodb container.
After doing so, restart the container by `docker-compose up --detach --build arangodb`.

Also stop the node backend process and start it again so that the new credentials are read from
the config file. You may use the `service.sh` script from this repo.

### Upgrade ArangoDB

Sometimes you may want to upgrade the Arango DB. In my `docker-compose.yml` file I use the latest
image "arangodb". In case you have a specific version there, you first should change that entry to
the new image version that you want to use.

After you have done the setup to pull the new image, the following steps can be done:

1. Stop the containers `docker-compose down`
1. Remove the arangodb image  `docker image list | grep arangodb | awk '{print $3}' | xargs docker rmi`
1. Restart the docker images `docker compose up -d` which will pull the new arangodb image
   However, it will probably not come up because the database files are older than the binary.
   Check this out with `docker ps` and you probably see the nginx and letsencrypt containers running.
1. Run the db upgrade process `docker-compose run --rm arangodb arangod --database.auto-upgrade`.
   Look at the output, this should upgrade your db files and also start the container successfully.
1. Restart MoodleNet (e.g. with the `service.sh` script)

The service name (in this case `arangodb`) is the name used in the docker-compose.yml file which
is used in the next lower level after *service:*.

If everything worked out correctly, you have your installation running. In the webadmin of the
database you can see the version number, that should be different from before.

### Database dump

To dump the complete database content from your Aragno DB, you may do the following:

```
docker exec  mn-arangodb sh -c 'rm -rf /dump && arangodump --all-databases'
t=arango-dump-$(date +%Y-%m-%d-%H-%M); docker cp mn-arangodb:/dump $t
```

In case you have set a password for your root account, you must provide it like this:

```
docker exec  mn-arangodb sh -c 'rm -rf /dump && arangodump --server.password "my-secret" --all-databases'
```

This makes use of the `arangodump` command, which must be run inside the container.
In the second step, a local directory is created and the dumped files inside the container
are copied to the host machine.

The container name *mn-arangodb* is taken from the `docker-compose.yml`. If you use a
different name there, please adjust the name of the container in these two commands.

### Database retore

If you have created a backup with the mentioned method above, you can restore it with
the following commands:

```
docker exec -it mn-arangodb sh -c 'rm -rf /dump'
docker cp arango-dump-2024-06-19-12-45/dump mn-arangodb:.
docker exec -it mn-arangodb sh -c 'arangorestore --all-databases'
```

Note: the restore with a root password works like the dump command.

When a backup is created all relevant files are inside the `dump` directory. This
directory must be copied from your backup dir into the docker container in the
root directory. First the possibly previously created dump directory is deleted.
In the next step the dumped data is copied inside the container into `/dump`.
Form there the `arangorestore` tool reads the data and writes it into the
database.

Note: in the backup and restore process no passwords are used, I did this
for the dev system only.

## Nginx

### Adapt changes to Nginx

Sometimes you need to make changes to the webserver reverse proxy (e.g. add a user to the
admin access, add an entry to the black list). Changes must be done on the config of the
server itself.

Reload Nginx after you have changed the configuration:
```
docker exec -it mn-nginx-rv-proxy nginx -s reload -c /etc/nginx/nginx.conf
```

From outside the Nginx container, watch logs by:
```
docker logs <container_id> --follow
```
or without to have the container id:
```
docker ps | grep nginx | cut -d \  -f 1 | xargs docker logs --follow
```

The container id can be obtained from the output of `docker ps`.

### Rebuild the container

**Note**: If you want to keep the changes persistent, you should also change the files
within the docker setup (the content that was copied from the directory `docker_setup`
in this repo - the nginx files reside in `docker_setup/data/nginx`) so that these changes
are included in the setup in case containers are rebuilt.

This is also necessary when you change anything at the `docker-compose.yml` file (in this case for nginx).

To rebuild just the nginx container do the following:

```
docker compose down nginx
docker compose up -d --build  nginx
```

The first command stops the container. The second command rebuilds the container and then starts
it in daemon mode.

### Manual

For our instance we want to have a manual for the platform so that the user has a reference on how
to use the platform e.g. how to login in, downloading or even uploading and publishing a resource.

The idea is to display some manual pages at a link that is within the platform. Since we have a running
nginx as a reverse proxy we could use that webserver to simply serve some additional html files and images
that are located outside of the node application in a random directory on the server.

The html site is build elsewhere and then uploaded into a directory on the server. In my case this is
`/home/oer/manual`. This directory must be included in the `nginx` service as an extra volume share. The
`docker-compose.yml` has to be extended by the line `./manual:/var/www/manual` in the section
`services.nginx.volumes`. You may adapt the source path for your setup.

In addition the nginx config needs to be extended by the following directives:

```
location /manual/ {
    alias /var/www/manual/index.html;
}

location /manual {
    return 301 /manual/index.html;
}

location ~ ^/manual/(.*?)$ {
    alias /var/www/manual/$1;
}
```

This ensures that `https://oer.example/manual/index.html` serves the manual pages. The first directive is the
abbreviation for the directory with trailing slash. The second directive is the abbreviation for the directory
without the trailing slash. The last directive serves all files below `/manual/` for the corresponding request.
This includes the main `index.html` as well as any image that is embedded in the page and in the same or a sub
directory.
