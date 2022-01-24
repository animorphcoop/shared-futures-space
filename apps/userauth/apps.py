# pyre-strict
import sys
from django.apps import AppConfig


class UserauthConfig(AppConfig):
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'userauth'
    def ready(self) -> None:
        if 'runserver' in sys.argv:
            from .models import CustomUser
            # the user that sends system messages
            CustomUser.objects.get_or_create(id=0, display_name = 'notifications') #pyre-ignore[16]
