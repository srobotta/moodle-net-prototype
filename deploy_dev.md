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
conjunction with the dev environment - it works in the production environment).
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
* Restart the MoodleNet service (try to kill any npm processes, restart MoodleNet with the provided command)
  and check if the site is reachable.
* Delete and/or tar older release directories (this may take a while).

Note: When the server is restarted, the compiled webapp seems missing (because of the database setting?) and
needs to be rebuilt. This, of course, is usually done with a separate `npm` task. Therefore, we copy the recently
created webapp into the correct directory **after** the service is started. Upon the first call, the app is rebuilt
by the request. Thus, the deploy-script does several curl calls to check whether the
service is up and running again.

Adjustments to the script need to be done for all vaiables that are in capital letters. On the other hand,
some assumptions are taken, which might not exactly fit your infrastructure. In this case please make the
required adjustments also in the deploy script itself, or report it here to make the script more flexible.

Todo:
* use enivronment variables or a text file for the configuration variables.
* have an restore script that reverts back to a certain release.
* Make the script work smoothly -> at the moment there are a few glitches so that it does not run out of the box, especially bring up the service while the webapp is missing. See below for troubleshooting.

### Troubleshooting

Although mostly automated, the deployment process does not aways run smoothly from start to end.

#### Server does not come up

After the deployment the npm process is killed and the service is then started again. This takes a while
and the deploy script checks several times for a 200 response. If that does not work, the service hungs
because of a missing webapp.

```
Try to reach https://oer.example.org ... failed with response 502
Retry ... failed with response 502
Retry ... failed with response 502
Retry ... failed with response 504
Retry ... failed with response 504
Retry ... failed with response 504
Retry ... failed with response 504
Retry ... 

```

Login with another shell, in the log of the current process started with `nohup` the error can be
spotted:

```
tail nohup.out.32 

...
[Error: ENOENT: no such file or directory, open '/home/ubuntu/moodlenet-dev/.dev-machines/my-dev/fs/@moodlenet/react-app/webapp-build/latest-build/index.html'] {
  errno: -2,
  code: 'ENOENT',
  syscall: 'open',
  path: '/home/ubuntu/moodlenet-dev/.dev-machines/my-dev/fs/@moodlenet/react-app/webapp-build/latest-build/index.html'
}

```

Then just copy manually the freashly build webapp code at the correct place like the deploy script
would do:
```
 p -r moodlenet-release-32/react-app_latest-build/* moodlenet-dev/.dev-machines/my-dev/fs/@moodlenet/react-app/webapp-build/latest-build/.
```

When you call now the url once more, the page should show up immediately because the built is there.

#### Missing changes in the webapp

When you develop locally and use the watch process from the webapp, the webapp is build immediately.
However, what is deployed comes acctually from some other place (te experiences developer may give me
some enlightment on how to improve that).

Basically before deploying the latest changes from the webapp make sure that these changes are visible
when you call http://localhost:8080. This is the backend service containing the latest webapp.
When the changes are not visible, the webapp has to be rebuilt.

1. Check that in the `default.config.json` the build of the webapp is enabled. The keys `pkgs.@moodlenet/react-app.noWebappBuilder` and
`pkgs.@moodlenet/react-app.noWebappServer` should be set to *false*.
1. Manipulate the last build entry in the database and set the hash
key and last built date so something else. The Arango DB can be reached
via the browser at http://localhost:8529/_db/moodlenet__react-app/_admin/aardvark/index.html#collection/Moodlenet_simple_key_value_store/build-info%3A%3A and looks like this: ![Arango DB last build information](mnet_last_built.png)
Change the red framed values and hit save at the bottom (not in screenshot).
Then call once again http://localhost:8080
On the console of the process you should see now output of the build
process and the page takes some time until it is displayed.


