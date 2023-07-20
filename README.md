# Shared Futures Space

## Development

This is a Django/Wagtail + Postgres + Redis + Celery stack.

### TypeScript

Make sure you have typescript installed globally for local development:

```
npm install -g typescript
```

Then, from the repo's root directory, each time you want to rebuild JS files after changing typescript ones,
you can run:

```
./ts_generate_js.sh
```

Note: Run `chmod +x ts_generate_js.sh` if file not executable.

To automatically watch changes in TypeScript files and re-generate, we use
[entr](https://github.com/eradman/entr). To run:

```sh
make watch
```

### Configuration

Before building, you might optionally want to make settings changes in `sfs/settings/local.py`.

If desired to use development or production mode (affects things like the debug tools), you might want to change
`.dev` to `.production` or vice versa in `sfs/settings/settings.py`.

### Docker setup

Linux & MINGW64 on Windows:

```sh
# build containers
USER_ID=$(id -u) GROUP_ID=$(id -g $whoami) docker-compose up --build
```

macOS:

```sh
# Mac has obfuscated groups for Docker, so we use user ID
# for Dockerfile group instead of group ID
USER_ID=$(id -u) GROUP_ID=$(id -u) docker-compose up --build
```

Windows (running Linux containers):

```sh
USER_ID=$(1000) GROUP_ID=$(1000) docker-compose up --build
```

### Commands

Enter shell:

```sh
docker-compose exec app sh
```

Run Django-related administrative commands:

```sh
docker-compose exec app django-admin startapp healerapp
# OR
docker-compose exec app python3 manage.py startapp healerapp
```

Create superuser:

```sh
docker-compose exec app python3 manage.py createsuperuser
```

Install tailwind theme:

```sh
docker-compose run app python3 manage.py tailwind install
```

Collect static:

```sh
docker-compose exec app python3 manage.py collectstatic
```

Migrations:

```sh
docker-compose exec app python3 manage.py makemigrations && docker-compose exec app python3 manage.py migrate
```

Running Tests:

```sh
# all tests
docker-compose exec app pytest tests

# a specific one
docker-compose exec app pytest tests/test_account.py
# add `-s` flag to display output
docker-compose exec app pytest -s tests/test_account.py
```

NOTE: Test run automatically on Gitlab after a push.

Python black code formatting:

```sh
docker compose exec -it app make format
```

Python code linting:

```sh
docker compose exec -it app make lint
```

## Uploading Data

1. Fetch zip with autoupload directory to be dropped into repo's root: https://hub.animorph.coop/f/261269

2. Run:

```sh
docker-compose exec app ./manage.py upload_dev [filename.json]
```

3. Put data from [filename.json] in the db. Filename defaults to `upload_conf.json`, which contains some default debugging data.

Example with current file:

```sh
docker-compose exec app python3 manage.py upload_dev upload_conf_dev.json
# or
USER_ID=$(id -u) GROUP_ID=$(id -g $whoami) docker-compose exec app python3 manage.py upload_prod upload_conf_prod.json
```

## Resources and notes

### Product terminology

This of "rivers" as work projects, "swimmers" as project members, and "springs"
as areas where work can take place.

Each river is at a specific stage (envison, plan, act, reflect) at any given
time. Rivers progress directionally from one stage to another.

"Resources" are knowledge resources as links. "Salmon" is our helper bot.

### Directories description

* `apps/`: includes all Djano apps
* `search/`: Wagtail search views
* `sfs/`: Django project
* `templates/`: includes all Django HTML templates used across all Django apps
* `tests/`: Django tests using pytest

### Turning off and on again

Occasionally, issues with spinning new containers out of existing images might occur.

To stop containers and remove them along with images:

```
docker stop $(docker ps -a -q)
docker system prune -a
```

Alternatively, to start from a clean slate :

```
docker-compose build --force-rm --no-cache && docker-compose up
```

### Adding management commands

Management applies to the Django naming convention:

https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/

### Celery integration

http://celery.readthedocs.org/en/latest/django/first-steps-with-django.html

### Dockerfile venv path

Inspiration in regards to setting the path for venv in Dockerfile:

https://pythonspeed.com/articles/activate-virtualenv-dockerfile/

```
docker-compose exec app pip3 -V
# returns /home/app/venv/lib/python3.9/site-packages/pip (python 3.9)
```

### Directory structure

Changed directory structure to nest all apps within one dir:

* https://stackoverflow.com/questions/22841764/best-practice-for-django-project-working-directory-structure
* https://github.com/Mischback/django-project-skeleton/blob/development/project_name/settings/common.py

### New Celery tasks

When adding celery task, restarting its container is required.

### Mapping IPs onto Docker containers

We need to ensure that UID and GID from the system (host) are mapped onto the container user. The containers carry over
User and Group IDs as they share one kernel. So we need to ensure that IDs of the user and group of the host match these
of the container user.

References: 

* https://medium.com/@mccode/understanding-how-uid-and-gid-work-in-docker-containers-c37a01d01cf
* https://blog.dbi-services.com/how-uid-mapping-works-in-docker-containers/

### Passing variables to Dockerfile via docker-compose

Mapping the UID and GID will change depending on the environment, we don't want to change the Dockerfile each time.
Does look like it's challenging/dangerous to include shell in env variables, e.g. [Ref 1](https://github.com/docker/compose/pull/8078).
Hence need to pass the user variables via CLI when building the containers.

```
USER_ID=$(id -u) GROUP_ID=$(id -g $whoami) docker-compose up --build
```

### Tailwind

Following [the documentation](https://django-tailwind.readthedocs.io/en/latest/installation.html),

After pulling, need to execute npm install once as node_modules are in gitignore:

```
docker-compose exec app python3 manage.py tailwind install
```

Then run in a separate terminal session to listen for changes:

```
docker-compose exec app python3 manage.py tailwind start
```

To build for production, run:

```
docker-compose exec app python3 manage.py tailwind build
```

Note: Styles passed dynamically from views are not automatically applied to tailwind classes (which are exported as
static classes at the time of save/build). So even if the classes are on the list in tailwind.confg.js, but they are
not used by any html element at the time of running the app you cannot refer to them.

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

### Deployment

**NOTE:** Before using in a public-facing environment, don't forget to change the default credentials! They're in
`variables.env`, `sfs/settings/local.py` and `.gitlab_ci.yml`

**NOTE:** DON'T FORGET TO CHANGE FROM THE DEFAULTS IN THE PROD SERVER BEFORE RELEASE, BECAUSE THE CURRENT ONES ARE IN
THE GIT HISTORY
