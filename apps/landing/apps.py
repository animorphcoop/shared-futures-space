from django.apps import AppConfig


class LandingConfig(AppConfig):
    default_auto_field: str = 'django.db.models.BigAutoField'  # in this version just suppresses a warning about deprecation
    name: str = 'apps.landing'
