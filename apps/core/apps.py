from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field: str = 'django.db.models.BigAutoField' # in this version just suppresses a warning about deprecation of the default value
    name: str = 'core'
