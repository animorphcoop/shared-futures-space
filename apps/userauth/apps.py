# pyre-strict
from django.apps import AppConfig


class UserauthConfig(AppConfig):
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'userauth'
