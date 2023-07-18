# How to deploy your own instance

This is a guide on how to deploy a new instance of Shared Futures Space on a
fresh Debian 11 installation.

This assumes you have root access.

## Update system

```sh
apt-get update
```

# Install docker

```sh
apt-get install ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo   "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

# Install Node.js LTS

```sh
curl -fsSL https://raw.githubusercontent.com/tj/n/master/bin/n | bash -s lts
npm install -g n
```

# Install caddy

```sh
apt-get install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt-get update
apt-get install caddy
```

To configure Caddy, replace /etc/caddy/Caddyfile with:

```
your-shared-futures-space.com:443 {
    route {
        file_server /static/* {
            root /var/www/sfs
        }
        reverse_proxy 127.0.0.1:9000
    }

    tls your@email.com {
        on_demand
    }

    encode zstd gzip
}
```

# Create deploy user

```sh
apt-get install git
adduser deploy  # empty password
```

# Clone repository

```sh
sudo -i -u deploy
cd /var/
mkdir www
cd www/
git clone https://git.coop:animorph-coop/shared-futures-space
```

# Configure instance

* Create `sfs/settings/secrets.py` with:
    * `SECRET_KEY`
    * `EMAIL_HOST_PASSWORD`
    * `FACEBOOK_CLIENT_ID`
    * `FACEBOOK_SECRET`
    * `GOOGLE_CLIENT_ID`
    * `GOOGLE_SECRET`
* Change `sfs/settings/settings.py` to import `from .production import *` instead of dev.
* Change `variables.env` away from default values.

# Initialise instance

```sh
USER_ID=$(id -u) GROUP_ID=$(id -g $whoami) docker-compose up --build
```
