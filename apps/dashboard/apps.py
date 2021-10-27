from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'dashboard'
