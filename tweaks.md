# Tweaks running MoodleNet


## Arango DB

### Webadmin

To access the Agango DB browser backend, simply navigate in your browser to
http://localhost:8529/

This also works if the server is remote. In this case I use ssh portforwarding
in this way `ssh -NL 8529:localhost:8529 user@moodlenet.server`.

### Upgrade ArangoDB

Sometimes you may want to upgrade the Arango DB. In my `docker-compose.yml` file I use the latest
image "arangodb". In case you have a specific version there, you first should change that entry to
the new image version that you want to use.

After you have done the setup to pull the new image, the following steps can be done:

1. Stop the containers `docker-compose down`
1. Remove the arangodb image  `ocker image list | grep arangodb | awk '{print $3}' | xargs docker rmi {}`
1. Restart the docker images `docker-compose up -d` which will pull the new arangodb image
   However, it will probably not come up because the database files are older than the binary.
   Check this out with `docker ps` and you probably see the nginx and letsencrypt containers running.
1. Run the db upgrade process `docker-compose run --rm arangodb arangod --database.auto-upgrade`.
   Look at the output, this should upgrade your db files.
1. Run `docker-compose up -d` to finally start the arangodb container.

### Database dump

To dump the complete database content from your Aragno DB, you may do the following:

```
docker exec  mn-arangodb sh -c 'rm -rf /dump && arangodump --all-databases'
t=arango-dump-$(date +%Y-%m-%d-%H-%M); docker cp mn-arangodb:/dump $t
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

**Note**: If you want to keep the changes persistent, you should also change the files
within the docker setup (the content that was copied from the directory `docker_setup`
in this repo - the nginx files reside in `docker_setup/data/nginx`) so that these changes
are included in the setup in case containers are rebuilt.