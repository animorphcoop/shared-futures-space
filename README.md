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

Migrations

```docker-compose exec app python3 manage.py makemigrations && docker-compose exec app python3 manage.py migrate```
---

- Adding management commands:
management applies to the django naming convention: https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/


- Celery integration: 
http://celery.readthedocs.org/en/latest/django/first-steps-with-django.html

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