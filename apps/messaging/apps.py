# pyre-strict
import sys
from uuid import UUID
from django.apps import AppConfig


class MessagingConfig(AppConfig):
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'messaging'
    def ready(self) -> None:
        if 'runserver' in sys.argv:
            from .models import Chat
            # the chat where requests for account changes go
            Chat.objects.get_or_create(id=0, uuid=UUID('00000000-0000-0000-0000-000000000000')) #pyre-ignore[16]
