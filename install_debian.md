# Install MoodleNet on a naked Ubuntu/Debian

You can basically copy and paste the commands (include the newlines) into a terminal
of your machine. The commands are taken from the linked documentation but stripped to
the necessary only (e.g. no need to purge old docker versions e.g. docker.io)
because on a minimal OS installation no additional packages or other software should
be installed.

## Docker

Info: https://docs.docker.com/engine/install

Add Docker's official GPG key:
```
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

Add the repository to apt sources:
```
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```
**Note**: for Ubuntu please change the link https://download.docker.com/linux/debian/ into
https://download.docker.com/linux/ubuntu

Install packages:
```
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
"deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
"$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update



## Node

Info: https://github.com/nodesource/distributions

Download and import Nodesource GPG key:
```
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
```

Create deb repository:
```
NODE_MAJOR=16
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
```

Install packages:
```
sudo apt-get update
sudo apt-get install nodejs
```

## MoodleNet

Info: https://docs.moodle.org/dev/MoodleNet

Start Arango DB via Docker:
```
sudo docker run -d --restart unless-stopped -e ARANGO_NO_AUTH=1 -p 8529:8529 --name=mn-3-db arangodb:3.10
```

Install and run MoodleNet:
```
npm create @moodlenet@latest moodlenet
cd moodlenet
npm start
```

MoodleNet is now accessible on the machine at http://*\<ip>*:8080