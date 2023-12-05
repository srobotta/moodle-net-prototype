# Setup MoodleNet for a development environment

The development environment follows much like the
[setup for the production environment](docker_setup.md). The main difference
is building the MoodleNet application itself.

## Overview

Following this guide you should get a MoodleNet installation ready for use in a
development environment. The Moodle Net Application is based on Node.js and is
running on the host directly listening on port 8080. After some tries I was not
able to put the MoodleNet application itself into a docker container as well,
to be used in the development environment. The problems were a rather
complicated setup with building the app inside the container.

The dev environment uses these three docker containers:

* [Arango DB](https://hub.docker.com/_/arangodb)
* Nginx Reverse Proxy that handles connections on port 80
* [Mailpit](https://hub.docker.com/r/axllent/mailpit) to simulate emails sending

## Requisites

Before your start, you should have your machine running with docker and nodejs installed.

To get the dev machine ready to start, follow the guide 
[Install MoodleNet on a naked Ubuntu/Debian](./install_debian.md) excluding
the point where MoodleNet is set up.

In addition I prepared my setup that I have a domain *oer.local* that I will use
for my dev environment.

To make this work, add the following to your `/etc/hosts` file:
```
127.0.0.1	oer.local
```

## Setup

Once you have installed Docker and nodejs we may start with the setup here to get the containers
running and MoodleNet installed.

### Application and Docker container

1. Create a new directory on your machine (e.g. `mkdir moodle-net-docker`)
1. Copy the content of the directory `docker_setup_dev` of this repository onto your machine
into that newly created directory.
1. Change into the directory so that you are at the same level where the
`docker-compose.yml` is located.
1. Run `docker-compose up -d` to build the containers and start them up.

If the container are running, the output of `docker ps` should list three
running containers.

### MoodleNet Code

Before starting here, make sure that you have node.js in version **16** running.

Somewhere on your machine checkout the
[MoodleNet project](https://github.com/moodle/moodlenet) via git:
```
git clone git@github.com:moodle/moodlenet.git
```

Change into that newly created folder `moodlenet` and initialize the project
e.g. install the dependencies:
```
npm install
```

Create a development server in an arbitrary directory (here we choose `my-dev`)
that is created inside the project in `.dev-machines`:
```
npm run dev-install-backend my-dev
```

Once this is done, the newly created `.dev-machines/my-dev/default.config.json`
needs to be changed:

- Build the web application as well.
- Adapt the mail settings to use mailpit.
- Change the hostname to oer.local although this is not necessarily required.

Apply the changes from the patch file `config.json.patch` manually or run
```
patch .dev-machines/my-dev/default.config.json config.json.patch
```

Now run the service:
```
npm run dev-start-backend my-dev
```

and check the result by typing "http://oer.local" into your browser.

If you do not want to use the reverse proxy you may directly use
http://localhost:8080.

### E-Mail

To test the emails sent from MoodleNet we have the mailpit container running.
All mails that are send from MoodleNet (see config above) are send via
localhost:1025 which is the SMTP port provided via the docker container.

The mails can be checked using the webfrontend of
[mailpit](https://github.com/axllent/mailpit) which is accessible
at http://localhost:8025.

## Development

To have a setup running for the development process the following is recommended:
* Run `npm run dev-start-backend my_dev` to have the node backend running
* Run `npm run dev-start-webapp my.dev` to have the react frontend running. The frontend
is accessible at http://localhost:3000 (that's also mentioned in the console - actually the browser
should be launched automatically to point you to the correct location.
* Run `npm run dev-assistant` to have assets copied to the correct location.
* Run `npm run prj-build-watch` to rebuild the app when changing any jsx or similar file.

All these processes must run in a different terminal, so you have 4 terminals open. It's always a good
choice to have a glance at these terminals from time to time. If something is not working as expected
you may spot the error inside the output in the terminal.

If the webapp is not starting because of a missing `_resolve-alias_.json` then check that the keys are
set to false:
* pkgs["@moodlenet/react-app"]["noWebappServer"]: false
* pkgs["@moodlenet/react-app"]["noWebappBuilder"]: false

You find them in the `default.config.json` and if you follow the steps above, the patch should have made
these changes already. This will also not be necessary some time in the future.


### Copy assets via lerna task

If you change images/icons etc. you may need to run `npx lerna run copy-assets` so that these are
placed at the correct location. This might be also the case if the webapp doesn't start because of missing
asset files. At any point in the future this will be changed.


## Tweeks

### Arango DB Webadmin

To access the Agango DB browser backend, simply navigate in your browser to
http://localhost:8529/

### Adapt changes to Nginx

Since Nginx runs in a docker container like on the productive environment
the config changes and restarts are done in the same way as described
[for the productive environment](docker_setup.md#adapt-changes-to-nginx)
