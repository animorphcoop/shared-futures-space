# Shared Futures Space

A project management platform where your community collaborates and gets stuff
done.

The original codebase was developed by Animorph Co-operative under community
engagement lead by the consortium partners: Co-operation Ireland, Belfast
Interface Project, University of Essex and Donegal Youth Service. This project
was supported by the European Union’s PEACE IV Programme, managed by the Special
EU Programmes Body (SEUPB).

## Development

This is a Django + Wagtail + Postgres + Redis + Celery stack. We use Docker
and Docker Compose to setup a development environment.

### Docker

Linux & MINGW64 on Windows:

```sh
# build containers
USER_ID=$(id -u) GROUP_ID=$(id -g $whoami) docker compose up --build
```

macOS:

```sh
# Mac has obfuscated groups for Docker, so we use user ID
# for Dockerfile group instead of group ID
USER_ID=$(id -u) GROUP_ID=$(id -u) docker compose up --build
```

Windows (running Linux containers):

```sh
USER_ID=$(1000) GROUP_ID=$(1000) docker compose up --build
```

This will start the stack in dev mode, though without frontend assets.
Continue in the section below to setup styles and JavaScript.

### TypeScript

We use [vite](https://vitejs.dev/) for bundling our typescript.

Make sure you have npm and nodejs installed, then install the dependencies:

```
npm install
```

To run in dev mode:

```
npm run dev
```

(or `make watch` will also run the same thing)

This will start a server that’s only serving static files. To see the app
locally go to http://127.0.0.1:9000

#### Building assets for production

To build the files run:

```
npm run build
```

It will build the assets into `sfs/vite-build`.

Inside the build directory it'll put:
- `manifest.json` used to connect ts paths to build js files
- all the build `.js` files with their full path (+ a file hash)

In production `vite_asset <path>` will use `manifest.json` to lookup the path to
the built `.js` file.

This directory is registered as a django static dir, so when collectstatic is
run, it will include those resources.

The built files will be served as normal django static assets.

### Commands

Enter shell:

```sh
docker compose exec app sh
```

Run Django-related administrative commands:

```sh
docker compose exec app django-admin startapp healerapp
# OR
docker compose exec app python3 manage.py startapp healerapp
```

Create superuser:

```sh
docker compose exec app python3 manage.py createsuperuser
```

Collect static:

```sh
docker compose exec app python3 manage.py collectstatic
```

Migrations:

```sh
docker compose exec app python3 manage.py makemigrations && docker compose exec app python3 manage.py migrate
```

Running Tests:

```sh
# all tests
docker compose exec app pytest tests

# a specific one
docker compose exec app pytest tests/test_account.py
# add `-s` flag to display output
docker compose exec app pytest -s tests/test_account.py
```

Python black code formatting:

```sh
docker compose exec -it app make format
```

Python code linting:

```sh
docker compose exec -it app make lint
```

## Development data

Follow these instructions to fill a development database with some example
content.

1. Fetch zip with autoupload directory to be dropped into repo's root: https://hub.animorph.coop/f/261269

2. Run:

```sh
docker compose exec app python3 manage.py upload_dev upload_conf_dev.json
# or
USER_ID=$(id -u) GROUP_ID=$(id -g $whoami) docker compose exec app python3 manage.py upload_prod upload_conf_prod.json
```

## Deployment

We use [Ansible](https://docs.ansible.com/ansible/latest/) to provision
production machines. To setup:

1. Acquire ssh access into a machine.
1. `cp ansible/.envrc.example ansible/.envrc`
1. Edit `ansible/.envrc` with your details and settings.
1. Run the playbook with:

```sh
cd ansible/
source .envrc
ansible-playbook playbook.yaml -v -e @vars.yaml
```

You can also run the following as an ssh check into your machine:

```sh
ansible all -m ping
ansible-inventory --list
```

## Resources and notes

### Product terminology

This of "rivers" as work projects, "swimmers" as project members, and "springs"
as areas where work can take place.

Each river is at a specific stage (envison, plan, act, reflect) at any given
time. Rivers progress directionally from one stage to another.

"Resources" are knowledge resources as links. "Salmon" is our helper bot.

### Directories description

* `apps/`: includes all Django apps
* `search/`: Wagtail search views
* `sfs/`: Django project root
* `templates/`: includes all Django HTML templates used across all Django apps
* `tests/`: Django tests using pytest

### Directory structure

All Django apps are nested within one dir, `apps`,

### New Celery tasks

When adding celery task, restarting its container is required.

### Mapping IPs onto Docker containers

We need to ensure that UID and GID from the system (host) are mapped onto the
container user. The containers carry over User and Group IDs as they share one
kernel. So we need to ensure that IDs of the user and group of the host match
these of the container user. This behaviour is different in macOS as it
automatically maps container file ownership to that of the host.

References: 

* https://medium.com/@mccode/understanding-how-uid-and-gid-work-in-docker-containers-c37a01d01cf
* https://blog.dbi-services.com/how-uid-mapping-works-in-docker-containers/
* https://stackoverflow.com/a/61009413/5631104

### Passing variables to Dockerfile via docker compose

Mapping the UID and GID will change depending on the environment, we don't want
to change the Dockerfile each time. Does look like it's challenging/dangerous to
include shell in env variables, e.g.
[Ref 1](https://github.com/docker/compose/pull/8078).
Hence need to pass the user variables via CLI when building the containers.

```
USER_ID=$(id -u) GROUP_ID=$(id -g $whoami) docker compose up --build
```

### Tailwind

Tailwind is include in the vite config, via PostCSS.

Note: Styles passed dynamically from views are not automatically applied to
tailwind classes (which are exported as static classes at the time of
save/build). So even if the classes are on the list in tailwind.config.js, but
they are not used by any html element at the time of running the app you cannot
refer to them.

### Social account login

To use social account logins, add the following to local.py:

```
from .base import INSTALLED_APPS

INSTALLED_APPS += [
    'allauth.socialaccount.providers.google'
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': '...',
            'secret': '...',
            'key': ''
        }
    }
}
```

Also, make sure `ENABLE_ALLAUTH_SOCIAL_LOGIN = True` is present on your settings
file.
