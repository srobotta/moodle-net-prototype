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

Before starting here, make sure that you have node.js in version **20** running.

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

Whenever you switch branches and want to develop on the application the following
steps should be followed:

1. (Optional) clean the old vendor directory and build files from a former branch:
```
npm run prj-cleanup-all
rm -rf node_modules
```

2. Reinstall packages:
```
npm install
```

3. Copy assets:
```
npx lerna run copy-assets
```

4. Start the backend server (node process, accessible at http://localhost:8080):
```
npm run dev-start-backend my-dev
```

5. Start the webapplication in a new terminal (react frontend, accessible at http://localhost:3000):
```
npm run dev-start-webapp my-dev
```

6. Start the watch task in a new terminal:
```
npm run prj-build-watch
```

If something is not working as expected you may spot the error inside the output in the
terminal.

If the webapp is not starting because of a missing `_resolve-alias_.json` then check
that the keys are set to false:
* pkgs["@moodlenet/react-app"]["noWebappServer"]: false
* pkgs["@moodlenet/react-app"]["noWebappBuilder"]: false

You find them in the `default.config.json` and if you follow the steps above,
the patch should have made these changes already. This will also not be necessary some time in the future.

### Copy assets via lerna task

If you change images/icons etc. or the webapp cannot be started because of missing
some *.svg or similar files, then you may need to run `npx lerna run copy-assets` so
that these are placed at the correct location.

This may change in future at any point because assets should be copied automatically
in the build process.

### Missing scss files

When installing a fresh MoodleNet, at the very first time the webapp may not be compiled
because of missing scss files (check the output at the console). In this case the
following files need to be copied from the `src` directory to the `dist` directory:

```
cd packages/extensions-manager
cp src/webapp/components/organisms/ExtensionsList/ExtensionsList.scss dist/webapp/components/organisms/ExtensionsList/.
cp src/webapp/components/pages/ExtensionInfo/ExtensionInfo.scss dist/webapp/components/pages/ExtensionInfo/.
cp src/webapp/components/pages/Extensions/Extensions.scss dist/webapp/components/pages/Extensions/.
cp src/webapp/components/pages/ManageExtensions/ManageExtensions.scss dist/webapp/components/pages/ManageExtensions/.
```

Going back to the main directory and running `npm run dev-start-backend my-dev` should start the backend and this
time compile the webapp.