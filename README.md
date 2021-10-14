# Shared Futures Space
## Django/Wagtail + Postgres + Redis + Celery

- Build containers
```docker-compose up --build```


- Starting an app
```docker-compose run app sh -c "django-admin startapp NAME"```

- Adding management commands:
management applies to the django naming convention: https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/

- Celery integration: 
http://celery.readthedocs.org/en/latest/django/first-steps-with-django.html
