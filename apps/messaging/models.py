# pyre-strict

from userauth.models import CustomUser # pyre-ignore[21]
from django.db import models
from uuid import uuid4

class Message(models.Model):
    uuid = models.UUIDField(default = uuid4, editable = False)
    timestamp = models.DateTimeField()
    sender = models.ForeignKey('userauth.CustomUser', null = True, on_delete = models.SET_NULL)
    text = models.CharField(max_length = 2000)
    # snippet =
    chat = models.ForeignKey('messaging.Chat', on_delete = models.CASCADE)

class Chat(models.Model):
    uuid = models.UUIDField(default = uuid4, editable = False)
