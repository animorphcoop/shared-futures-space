# Shared Futures Space
## Django/Wagtail + Postgres + Redis + Celery

- Build containers
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

