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

### Application and Docker container

1. Create a new directory in (e.g. the users home directory) where the MoodleNet application
is installed and holds the data.
1. Copy the content of the directory `docker_setup` of this repository onto your machine
into that newly created directory.
1. Change into the directory so that you are at the same level where the `init-letsencrypt.sh`
and the `docker-compose.yml` are located.
1. In the file `ini-letsencrypt.sh` replace *example.org* and *www.example.org* with your
own domain. Also add an email address 3 lines below the domain list.
1. In the file `data/nginx/app.conf` replace all occurrences of *example.org* to your domain.
1. Run the script by `sudo ./init-letsencrypt.sh`.

Once you have a certificate then run `docker-compose up -d` to build the rest of the containers
and have them started.

### Systemd Service

For an easier way of starting and stopping the MoodleNet app and especially to have it
launched automatically when the server is rebooted, a systemd service entry should be
created.

To have a systemd service link create the file `/etc/systemd/system/moodlenet.service` with
the following content:
```
[Unit]
Description="MoodleNet"

[Service]
User=ubuntu
ExecStart=npm start
WorkingDirectory=/home/ubuntu/moodlenet
Restart=always
RestartSec=5
#StandardOutput=append:/home/ubuntu/moodlenet-logs/info.log
#StandardError=append:/home/ubutnu/moodlenet-logs/error.log
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=MoodleNet

[Install]
WantedBy=multi-user.target

```

In this case the user account is *ubuntu* and the MoodleNet application is installed in
the users home directory into `moodlenet`.

Once you have created the new file for the service, reload the systemd daemon
to be aware of the new service:
```
sudo systemctl daemon-reload
```

Start MoodleNet:
```
sudo systemctl start moodlenet
```
Check the status of the service:
```
sudo systemctl status moodlenet
```
Stop the service by:
```
sudo systemctl stop moodlenet
```

If the MoodleNet service doesn't start for any reason or if you would like to check the
logs, then do:
```
less /var/log/syslog | grep MoodleNet
```

### E-Mail

MoodleNet wants to send emails, especially when you register yourself, so that you can
confirm your email address. To do so, edit the `default.config.json` file in the MoodleNet
installation directory and add/change the email setting to something like this:
```
"@moodlenet/email-service": {
  "nodemailerTransport": {
      "host": "smtp.example.org",
      "port": 465,
      "secure": true,
      "auth": {
          "user": "mail@myservice.org",
          "pass": "somepass"
      },
      "logger": true,
      "debug": true
  }
},
```

If you prefer the SMTP string you would do:
```
"@moodlenet/email-service": {
  "nodemailerTransport": "smtps://mail%40myservice.org:password@smtp.example.org/"
},
```

Then restart the MoodleNet service (see above) and e.g. sign up a new user. To verify that
the email sending works you may check the logs.
```
Oct  2 09:55:26 moodlenet3 MoodleNet[99545]: [2023-10-02 09:55:26] DEBUG Creating transport: nodemailer (6.6.1; +https://nodemailer.com/; SMTP/6.6.1[client:6.6.1])
Oct  2 09:55:26 moodlenet3 MoodleNet[99545]: [2023-10-02 09:55:26] DEBUG Sending mail using SMTP/6.6.1[client:6.6.1]
Oct  2 09:55:26 moodlenet3 MoodleNet[99545]: [2023-10-02 09:55:26] DEBUG [0czWbf2sJQA] Resolved smtp.example.org as XX.XX.XXX.XX [cache hit]
Oct  2 09:55:26 moodlenet3 MoodleNet[99545]: [2023-10-02 09:55:26] INFO  [0czWbf2sJQA] Secure connection established to XX.XX.XXX.XX:465
Oct  2 09:55:26 moodlenet3 MoodleNet[99545]: [2023-10-02 09:55:26] DEBUG [0czWbf2sJQA] S: 220 smtp.example.org ESMTP ready
Oct  2 09:55:26 moodlenet3 MoodleNet[99545]: [2023-10-02 09:55:26] DEBUG [0czWbf2sJQA] C: EHLO [127.0.0.1]
Oct  2 09:55:26 moodlenet3 MoodleNet[99545]: [2023-10-02 09:55:26] DEBUG [0czWbf2sJQA] S: 250-smtp.example.org
Oct  2 09:55:26 moodlenet3 MoodleNet[99545]: [2023-10-02 09:55:26] DEBUG [0czWbf2sJQA] S: 250-SIZE 52428800
Oct  2 09:55:26 moodlenet3 MoodleNet[99545]: [2023-10-02 09:55:26] DEBUG [0czWbf2sJQA] S: 250-8BITMIME
Oct  2 09:55:26 moodlenet3 MoodleNet[99545]: [2023-10-02 09:55:26] DEBUG [0czWbf2sJQA] S: 250-PIPELINING
Oct  2 09:55:26 moodlenet3 MoodleNet[99545]: [2023-10-02 09:55:26] DEBUG [0czWbf2sJQA] S: 250-HELP
Oct  2 09:55:26 moodlenet3 MoodleNet[99545]: [2023-10-02 09:55:26] DEBUG [0czWbf2sJQA] S: 250 AUTH LOGIN
Oct  2 09:55:26 moodlenet3 MoodleNet[99545]: [2023-10-02 09:55:26] DEBUG [0czWbf2sJQA] SMTP handshake finished
Oct  2 09:55:26 moodlenet3 MoodleNet[99545]: [2023-10-02 09:55:26] DEBUG [0czWbf2sJQA] C: AUTH LOGIN
...
Oct  2 09:55:26 moodlenet3 MoodleNet[99545]: [2023-10-02 09:55:26] DEBUG [0czWbf2sJQA] S: 235 2.0.0 OK
Oct  2 09:55:26 moodlenet3 MoodleNet[99545]: [2023-10-02 09:55:26] INFO  [0czWbf2sJQA] User "mail@myservice.org" authenticated
Oct  2 09:55:26 moodlenet3 MoodleNet[99545]: [2023-10-02 09:55:26] INFO  Sending message <a3a83f03-31dc-a412-e528-5ded3c24dd06@localhost> to <new.user@somewhere.org>
```
The line *User "mail@myservice.org" authenticated* tells us that the authentication was
successful and mails should be sent. Whether they are received is another issue. In this
example output it might happen that the mail was received in the spam folder because the from
address was not setup properly.

Be aware, here I am using port 465. Your provider might use 587 or some other port.

If the mailing works well, the `debug` and `logger` keys in the config might be removed to
stop logging the mail processing.

### Admin Area

After installing the admin area is password protected. The credentials are located in the
`data/nginx/.htpasswd` file. You may create new credentials using the following command:

```
htpasswd -n <username>
```
After entering the password on the command line, the output is one line that goes into the
`.htpasswd` file. To have several users, you can repeat the process with different user names.

If the htpasswd tool is missing on your system, you might install it by
`sudo apt install apache2-utils`.

There's one problem at the moment that't being discussed: with this setup it's currently
not possible to save changes to the settings, because from the MoodleNet
app the POST requests are missing the credentials.

The workaround/solution is to follow the steps
[described in the docs](https://docs.moodle.org/dev/MoodleNet#Default_authentication_system)
or in short here:
1. Create a new user (self signup)
2. Confirm that user by clicking the confirmation link in the email. If no email is received, 
enable logging and fetch the confirmation link from the logs.
3. Login as admin via *\<domain>/login/root* (password is in the `default.config.json` in
the key *@moodlenet/system-entities* -> *rootPassword*)
4. In the users list make that user an admin by clicking the icon.

## Tweeks

### Arango DB Webadmin

To access the Agango DB browser backend, create an ssh tunnel from your machine to
the MoodleNet server like `ssh -NL 8529:localhost:8529 user@moodlenet.server` and
then in the browser of your local machine navigate to http://localhost:8529/

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
in this repo) so that these changes are included in the setup in case containers are
rebuilt.




