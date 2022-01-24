# Shared Futures Space
## Django/Wagtail + Postgres + Redis + Celery

- Build containers
Since [Commit 6e3c8b4a](https://git.coop/animorph-coop/shared-futures-space/-/commit/6e3c8b4a6e5893e3a00379ba383c7c0cead397d0)
```USER_ID=$(id -u) GROUP_ID=$(id -g $whoami) docker-compose up --build```

*Originally:*
```docker-compose up --build```

- After cloning for the first time: 
- `git-crypt unlock` 
- (assuming your public key has been given access). See .gitattributes for the files this affects.


To enter shell
```docker-compose exec app sh```


To run Django-related administrative commands
```docker-compose exec app django-admin startapp healerapp```
OR
```docker-compose exec app python3 manage.py startapp healerapp```


Create superuser

```docker-compose exec app python3 manage.py createsuperuser```

```docker-compose exec app python3 manage.py collectstatic```

Migrations

```docker-compose exec app python3 manage.py makemigrations && docker-compose exec app python3 manage.py migrate```

Running Tests
```
$ docker-compose exec app pytest tests
$ pyre
```
(they'll also run automatically on gitlab after a push)

---

### Using Static Typing
The key to effective use of static typing is the principle *"make illegal states unrepresentable"*. The type of a variable should cover precisely the set of values
it's expected to have and nothing else - that is, if a variable taking some specific value would cause
an error, the type system should be used to ensure that it can't take that value. That way, most kinds
of errors become type errors, and type errors are (hopefully) caught before runtime. This approach
means thinking about what each variable really represents.

for instance, the type of a variable that stores a string which must be one of a set of known options should not be `str` but an [Enum](https://docs.python.org/3/library/enum.html) type encompassing the set of acceptable options. That way, the type checker can be used to guarantee that it will never be set to an illegal value.

#### The python type system in particular

A variable can be annotated when it is declared: `a_whole_number`**`: int`**` = 42`

A function can likewise be annotated at declaration, including its return type:

`def add(A`**`: float`**`, B`**`: float`**`)`**` -> float`**`:`

`  return A + B`

(a function with no `return` returns `None`)

Parametric and otherwise special types must be imported from the typing library ([docs](https://docs.python.org/3/library/typing.html)).
These include:
- `List[T]`, `Dict[T,S]` - lists of type T and dicts from T to S (eg. `List[int]` or `Dict[str,bool]`)
- `Tuple[T1,T2,...,Tn]` - the type of an n-tuple of the given types. You can write `Tuple[T,...]` (ellipsis is literal) for a tuple of any number of Ts
- `Union[T1,T2,...,Tn]` - the type of a value which is one of a set of types. eg. `Union[str, int, List[int]]` accepts strings, integers and lists of integers
- `Optional[T]` - equivalent to `Union[T, None]`
- `Any` - matches any value at all
- `TypedDict` - dicts with specific known keys, which can be used to construct custom types like so (apologies for very studenty example):
```
class LabelledBinaryTree(TypedDict):
  label: str
  left: Optional[LabelledBinaryTree]
  right: Optional[LabelledBinaryTree]

tree: LabelledBinaryTree =
  {'label': 'root',
   'left': { 'label': 'leaf 1', 'left': None, 'right': None },
   'right': { 'label': 'leaf 2',
             'left': None,
             'right': { 'label': 'leaf 3', 'left': None, 'right': None}}}
```
#### The type checker

run `pyre` to type check. The file `.pyre_configuration` must list the location of your python `site-packages` in its `search_path` key.
It will only type check functions that have their types declared, unless the file begins with `# pyre-strict`. If pyre is wrong about the type of something, you can suppress the error with `# pyre-ignore[n]` where n is the error type number that appears in the pyre output.

---

- Adding management commands:
management applies to the django naming convention: https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/


- Celery integration: 
http://celery.readthedocs.org/en/latest/django/first-steps-with-django.html

---

**NOTE: before using in a public-facing environment, don't forget to change the default credentials! They're in `app_variables.env`, `db_pg_variables.env`, `sfs/settings/local.py` and `.gitlab_ci.yml`**

---
Occasionally, issues with spinning new containers out of existing images might occur.


To stop containers and remove them along with images

```docker stop $(docker ps -a -q)```

```docker system prune -a```

Alternatively, to start from a clean slate 
```docker-compose build --force-rm --no-cache && docker-compose up```

---

Inspiration in regards to setting the path for venv in Dockerfile: https://pythonspeed.com/articles/activate-virtualenv-dockerfile/

```docker-compose exec app pip3 -V```
returns /home/app/venv/lib/python3.9/site-packages/pip (python 3.9)


---

Changed directory structure to nest all apps within one dir
https://stackoverflow.com/questions/22841764/best-practice-for-django-project-working-directory-structure
https://github.com/Mischback/django-project-skeleton/blob/development/project_name/settings/common.py


--- 
Editing and deleting accounts need to be address
current pattern : account/10/delete/



---

When adding celery task, restarting its container is required.

---

#### Mapping IPs onto Docker containers
We need to ensure that UID and GID from the system (host) are mapped onto the container user. The containers carry over User and Group IDs as they share one kernel.
So we need to ensure that IDs of the user and group of the host match these of the container user.
References [1](https://medium.com/@mccode/understanding-how-uid-and-gid-work-in-docker-containers-c37a01d01cf) [2](https://blog.dbi-services.com/how-uid-mapping-works-in-docker-containers/)

**Challenge: passing variables to Dockerfile via Docker compose**
Mapping the UID and GID will change depending on the environment, we don't want to change the Dockerfile each time.
Does look like it's challenging/dangerous to include shell in env variables, e.g. [Ref 1](https://github.com/docker/compose/pull/8078).
Hence need to pass the user variables via CLI when building the containers.
```USER_ID=$(id -u) GROUP_ID=$(id -g $whoami) docker-compose up --build```



---

#### Tailwind
Following [the documentation](https://django-tailwind.readthedocs.io/en/latest/installation.html)
- After pulling need to execute npm install once as node_modules are in gitignore:
```docker-compose exec app python3 manage.py tailwind install```
- Then run in a separate terminal session to listen for changes.
```docker-compose exec app python3 manage.py tailwind start```
- To build for production.
```docker-compose exec app python3 manage.py tailwind build```

Notes:
Styles passed dynamically from views are not automatically applied to tailwind classes (which are exported as static classes at the time of save/build). So even if the classes are on the list in tailwind.confg.js, but they are not used by any html element at the time of running the app you cannot refer to them.



---

#### TypeScript

- Make sure you have typescript installed globally for local development

```npm install -g typescript```

- Then, each time you want to rebuild js files after changing typescript ones, you can run

```./ts_generate_js.sh```

from the repo's root directory (run `chmod +x ts_generate_js.sh` if file not executable)



---

### DEPLOYMENT

to deploy:

- merge into staging
- make sure `.dev` is changed to `.production` in sfs/settings/settings.py
- wait for tests to run
- run deploy.sh locally
- don't forget: app\_variables.env, db\_pg\_variables.env and sfs/settings/local.py are replaced suring deployment with versions stored on the server in /home/dev/sites/dev\_data

to use social account logins, add the following to local.py:

```
from .base import INSTALLED_APPS

INSTALLED_APPS += [
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google'
]

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'APP': {
            'client_id': '...',
            'secret': '...',
            'key': ''
        }
    },
    'google': {
        'APP': {
            'client_id': '...',
            'secret': '...',
            'key': ''
        }
    }
}

```



---
DON'T FORGET TO CHANGE FROM THE DEFAULTS IN THE PROD SERVER BEFORE RELEASE, BECAUSE THE CURRENT ONES ARE IN THE GIT HISTORY



