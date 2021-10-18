# Shared Futures Space
## Django/Wagtail + Postgres + Redis + Celery

- Build containers
```docker-compose up --build```

- After cloning for the first time: 
- `git-crypt unlock` 
- (assuming your public key has been given access). See .gitattributes for the files this affects.



- Starting an app
- EVERY TIME use RUN a NEW container is started - https://stackoverflow.com/a/41436850
~~docker-compose run app sh -c "django-admin startapp NAME"~~

INSTEAD use:
docker-compose exec app sh


- Adding management commands:
management applies to the django naming convention: https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/


- Celery integration: 
http://celery.readthedocs.org/en/latest/django/first-steps-with-django.html

management applies to the django naming convention: https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/

---
TO RESET everything
docker stop $(docker ps -a -q)
docker system prune -a

docker-compose build --force-rm --no-cache && docker-compose up

/sfs/venv/bin/python 