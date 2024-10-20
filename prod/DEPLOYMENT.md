# Deployment on Debian 12

Deploy your own instance of Shared Futures! There are two main ways of achieving it, with Ansible or manually step by step. Please find both describe below as Option A and Option B.  For either of deployment avenues there are two prerequisites:
1. Get a Debian machine and its IP address.
2. Get a domain name and configure its DNS with the machine’s IP address.

*Both are written from the point of user with sudo permissions.*

There are some important post-deployment commands in the last section of the document that will help potential monitoring and debugging.

*Note that the details will differ on other OS distributions and may change on Debian 12 over time*.

## OPTION A - ANSIBLE (AUTOMATED)


#### Step 1 - Prepare Ansible

- Make a directory for Ansible files:
```
mkdir sfs && cd sfs
```

    
- Install Ansible:

```
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt install ansible 
```

- Create a vault with env data (will prompt for password):

```
ansible-vault create vault.yml
```

Enter the production variables:

```
production_password: your_secure_password

env_vars:
  DEBUG: 0
  DJANGO_VITE_DEV_MODE: 0
  DOMAIN_NAME: sharedfutures.space
  BASE_URL: https://sharedfutures.space
  SECRET_KEY: your-prod-secret-key123
  POSTGRES_DB: sfs_db
  POSTGRES_USER: sfs_user
  POSTGRES_PASSWORD: password
  POSTGRES_HOST: db_pg
  CELERY_BROKER_URL: redis://redis:6379
  CELERY_RESULT_BACKEND: redis://redis:6379
  ENABLE_ALLAUTH_SOCIAL_LOGIN: 0
  GOOGLE_CLIENT_ID: your-google-client-id
  GOOGLE_SECRET: your-google-secret
  EMAIL_HOST: mail.example.com
  EMAIL_HOST_USER: hi@example.com
  EMAIL_HOST_PASSWORD: your-email-password
  DEFAULT_FROM_EMAIL: hi@example.com
  WEATHER_API_KEY: your-weather-api-key
  MAPTILER_API_KEY: your-maptiler-api-key
```

End exit file with `:wq`

- Make Ansible playbook:

```
vi playbook.yml
```

- Copy contents of ../ansible/playbook.yml


- Create inventory

```
vi inventory
```

- Copy contents of ../ansible/inventory.yml


#### Step 2 - Run playbook

- Enter the command (will prompt for vault password):
```
sudo ansible-playbook -i inventory playbook.yml --ask-vault-pass
```

Fetch yourself a cuppa. When finished you will be able to access your domain with Shared Futures online!


## OPTION B - BASH (MANUAL) 


#### Step 1: Create the user and add to sudo

- Create a new user named production:

```sh
sudo useradd -m -s /bin/bash production
```

- Add to the group of sudo

```
sudo adduser production sudo 
```

- Confirm they are in sudo group

```
newgrp sudo
```

- Set a password for the production user:

```sh
sudo passwd production
```

- Switch to the production user:

```sh
sudo su - production
```

#### Step 2: Install Docker and Docker Compose

- Prerequisites:
- 
```sh
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

- Install Docker packages:

```sh
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

- In order not to rely on using `sudo` for docker commands:

```sh
sudo usermod -aG docker $USER
```

- To avoid having to log out, need to refresh the group

```
newgrp docker
```

#### Step 3: Install Caddy

- Add Caddy Repository:

```sh
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
```

- Install Caddy:
```sh
sudo apt install caddy
```


#### Step 4: Clone the Repository

#### Clone the repository in your target directory:

- Go to the sites directory (which you might need to create first):

```sh
mkdir -p /home/production/sites && cd /home/production/sites
```

- Clone production branch:

```
git clone --branch production https://github.com/animorphcoop/shared-futures-space.git
```

- Enter project directory:

```
cd shared-futures-space
```

#### Step 5 - setup node for frontend code bundling

- First need to install Node (v18 LTS):

```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
```

- Reload the shell for nvm to become available:

```
source ~/.bashrc
```

- Restart your terminal and continue and then run (in the same directory as previously):

```
nvm install 18
```

- Installing dependencies for frontend

```
npm install
```

- Build frontend assets:

```
npm run build
```

#### Step 6 - Setup Django environment variables

- Copy the environment file:

```sh
cp .env.example prod/.env.prod
cd prod
```

- Set the production variables:

```
vi .env.prod
```

*Importantly set first 2 to zero AND ensure your domain has been entered*

```
DEBUG=0
DJANGO_VITE_DEV_MODE=0
DOMAIN_NAME=sharedfutures.space
BASE_URL=https://sharedfutures.space
SECRET_KEY=your-prod-secret-key123
POSTGRES_DB=sfs_db
POSTGRES_USER=sfs_user
POSTGRES_PASSWORD=password
POSTGRES_HOST=db_pg
CELERY_BROKER_URL=redis://redis:6379
CELERY_RESULT_BACKEND=redis://redis:6379
ENABLE_ALLAUTH_SOCIAL_LOGIN=0
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_SECRET=your-google-secret
EMAIL_HOST=mail.example.com
EMAIL_HOST_USER=hi@example.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=hi@example.com
WEATHER_API_KEY=your-weather-api-key
MAPTILER_API_KEY=your-maptiler-api-key
```

Save with `:wq`

#### Step 7: Configure Caddy webserver

- Stop and disable default Caddy processes:

```
sudo systemctl stop caddy.service 
sudo systemctl disable caddy.service
sudo mv /etc/caddy/Caddyfile /etc/caddy/Caddyfile.default.backup
```

- Create the new Caddyfile:

```sudo
sudo vi /etc/caddy/Caddyfile
```

- Configure your Caddyfile with your domain:

```caddyfile
my.domain:443 {
    route {
        file_server /static/* {
            root /home/production/sites/shared-futures-space
        }
        file_server /media/* {
            root /home/production/sites/shared-futures-space
        }
        reverse_proxy 127.0.0.1:9000
    }

    tls email@your.domain
}
```
*Replace your.domain with your actual domain name and email@your.domain with your actual email address.*


- Correct potential formatting issues

```
sudo caddy fmt --overwrite /etc/caddy/Caddyfile
```

### Step 8: Restart Caddy with config

Restart Caddy to apply the new configuration:

```sh
sudo systemctl enable caddy
sudo systemctl start caddy
```

### Step 9: Build and Run the Containers

Make sure you are in `/home/production/sites/shared-futures-space/prod` directory. 

- Build and run your Docker containers using the production Compose file:

```sh
USER_ID=$(id -u) GROUP_ID=$(id -g) docker compose -f docker-compose.prod.yaml up -d --build
```

*First time round this will pull the images and build them. It will take some time.*

### Step 10: Set Up Systemd Service

- Create service file for launching docker containers on boot.

`sudo vi /etc/systemd/system/sfs.service`

- Paste the contents:

```ini
[Unit]
Description=Shared Futures Space
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
RemainAfterExit=yes
WorkingDirectory=/home/production/sites/shared-futures-space/prod
ExecStart=/usr/bin/docker compose -f /home/production/sites/shared-futures-space/prod/docker-compose.prod.yaml up -d
ExecStop=/usr/bin/docker compose -f /home/production/sites/shared-futures-space/prod/docker-compose.prod.yaml down
TimeoutStartSec=0
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

- Reload Systemd, enable, and start the Services:

```sh
sudo systemctl daemon-reload
sudo systemctl enable sfs
sudo systemctl start sfs
```

---

## Post-deployment - independently of the deployment option

#### Logs

- To see whether the service is up:

```
sudo systemctl status sfs
```

- Logs for sfs service will show whether containers started successfully (last 50 lines): 

```
sudo journalctl -u sfs -n 50
```

- More effective way to inspect Docker logs is to go to the root project directory and run:


```
docker compose -f prod/docker-compose.prod.yaml logs
```



- Probably the most important for monitoring the app logs is to display Django-specific logs (last 50 lines):

```sh
docker exec -it app tail -n 50 /home/app/sfs/logs/uwsgi.log
```

docker exec -it app tail -n 50 /home/app/sfs/logs/uwsgi.log


- To stop the platform (it will automatically start on boot, or use `start`)

```
sudo systemctl stop sfs
```


#### Backups


- Format for saving the database file.

```
docker exec -t CONTAINER_NAME pg_dump -c -U DATABASE_USER -d DATABASE_NAME > FILENAME.sql
```

- Example of saving data (ensure the directory you want to save the backup into exists):

```
docker exec -t db_pg pg_dump -c -U sfs_user -d sfs_db > ../backups/sfs-$(date --utc +%Y%m%d-%H%M%S).sql
```

- To import previously exported into the database, format (ensure the database shape matches):

```
docker exec -i CONTAINER_NAME psql -U DATABASE_USER -d DATABASE_NAME < FILENAME.sql
```

When restoring from backup remember that you also need to move over the media directory from your backed up project for the restored project to work fully.