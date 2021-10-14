Shared Futures Space
Django/Wagtail + Postgres

after cloning for the first time: `git-crypt unlock` (assuming your public key has been given access). see .gitattributes for the files this affects.

docker-compose up --build


Starting an app
docker-compose run app sh -c "django-admin startapp NAME"


management applies to the django naming convention: https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/
