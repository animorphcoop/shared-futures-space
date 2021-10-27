# pyre-strict
from django.apps import AppConfig


class LandingConfig(AppConfig):
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'apps.landing'
