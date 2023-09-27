# Setup MoodleNet for a productive environment

The following guide was created with the help of the article
[Nginx and Let’s Encrypt with Docker in Less Than 5 Minutes](https://pentacent.medium.com/nginx-and-lets-encrypt-with-docker-in-less-than-5-minutes-b4b8a60d3a71)
and the authors [repo on Github](https://github.com/wmnnd/nginx-certbot).

## Overview

Following this guide you should get a MoodleNet installation ready for use in a productive
environment. The Moodle Net Application is based on Node.js and is running on the host
directly listening on port 8080 (this is a TODO to put it into a container as well).

In addition, there are three docker containers:

* Arango DB
* Nginx Reverse Proxy that handles connections on port 80 and 443
* Certbot container to update the Lets encrypt SSL certificates

## Requisites

Before your start, you should have server running with docker and nodejs installed. Also, you
should have a domain pointing to the server so that for this domain a SSL certificate can be
setup.

To get the server ready to start, follow the guide 
[Install MoodleNet on a naked Ubuntu/Debian](./install_debian.md) excluding the point where
MoodleNet is set up.

The machine where you install MoodleNet should have 2GB of RAM and sufficient storage space.

## Setup

Once you have installed Docker and nodejs we may start with the setup here to get the containers
running and MoodleNet installed.

1. Copy the content from the directory `docker_setup` of this repository onto your machine.
1. Change into the directory so that you are at the same level where the `init-letsencrypt.sh`
and the `docker-compose.yml` are located.
1. In the file `ini-letsencrypt.sh` replace *example.org* and *www.example.org* with your
own domain. Also add an email address 3 lines below the domain list.
1. In the file `data/nginx/app.conf` replace all occurrences of *example.org* to your domain.
1. Run the script by `sudo ./init-letsencrypt.sh`.

Once you have a certificate then run `docker-compose up -d` to build the rest of the containers
and have them started.

## Tweeks

### Arango DB Webadmin

To access the Agango DB browser backend, create an ssh tunnel from your machine to
the MoodleNet server like `ssh -NL 8529:localhost:8529 user@moodlenet.server` and
then navigate in your local machine to http://localhost:8529/

### Adapt changes to Nginx

Sometimes you need to make changes to the webserver reverse proxy (e.g. add a user to the
admin access, add an entry to the black list). Changes must be done on the config of the
server itself.

Login to the Docker container (Nginx):
```
docker exec -it mn-nginx-rv-proxy sh
```

Reload Nginx after you have changed the configuration:
```
nginx -s reload -c /etc/nginx/nginx.conf
```

From outside the Nginx container, watch logs by:
```
docker logs <container_id> --follow
```

The container id can be obtained from the output of `docker ps`.




