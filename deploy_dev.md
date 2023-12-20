# Deploy a MoodleNet custom environment

## Preface

Note: I am a less experienced developer in the node.js environment. Therefore,
the approach described here, might not the intended way to do it.

The use case for this approach is: I can locally develop my MoodleNet
instance (having a fork from the master repo) and then deploy my changes
onto a public accessible installation.

## Prerequisites

The setup of the live MoodleNet installation is a mixture as described in
the setup MoodleNet for a [development](docker_setup_dev.md) and the
[production](docker_setup.md) environment. From the production we use all
setup that is not the MoodleNet code. The MoodleNet code needs to be the changeset
that is in our repo and not coming from the public npm repository.

### General Setup

On the server I placed the code of MoodleNet into a directory called `moodlenet-dev`.
However, this is a symbolic link to the actual release. When a deployment is done
the code is copied into a new directory containing the release number. The symbolic
link of `moodlenet-dev` is then adjusted to the new release dir.

The node server needs to be started with `npm run dev-start-backend my-dev` and not
like in production with `npm start`.

### Start/Stop script for systemd

For some reason with the systemd script the MoodleNet service couldn't be reliably restarted (in
conjunction with the dev environment - it works in the production environment.
Therefore, I went another way to run npm myself with `nohup npm run dev-start-backend my-dev &`.
This can also be executed in a terminal and then closing the connection and the service is running
further.

### Deploy process

The whole effort to deploy a MoodleNet dev installation onto a public server is in the script `deploy-dev.sh`.

The deploy-script simply does the following:
* Create a new release number (this is a natural number that's increased by one during every deployment).
* Copy everything into a new release directory based on that release number. Several files can be omitted
  (with the `--exclude` flag).
* On the server link the uploaded dir with the new release dir.
* Restart the MoodleNet service (with the systemd script) and check if the site is reachable.

Note: When the server is restarted, the compiled webapp seems missing (because of the database setting?) and
needs to be rebuilt. This, of course, is usually done with a separate nom task. Therefore, we copy the recently
created webapp into the correct directory **after** the service is started. Upon the first call, the app is rebuilt
by the request. Thus, the deploy-script does several curl calls to check whether the
service is up and running again.

Adjustments to the script need to be done for all vaiables that are in capital letters. On the other hand,
some assumptions are taken, which might not exactly fit your infrastructure. In this case please make the
required adjustments also in the deploy script itself, or report it here to make the script more flexible.

Todo:
* use enivronment variables or a text file for the configuration variables.
* have an restore script that reverts back to a certain release.
* Make the script work smoothly -> at the moment there are a few glitches so that it does not run out of the box,
especially the restart of the mode js server.
