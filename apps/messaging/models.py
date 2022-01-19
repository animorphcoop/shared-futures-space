# pyre-strict

from django.db import models
from uuid import uuid4

class Message(models.Model):
    uuid = models.UUIDField(default = uuid4, editable = False)
    timestamp = models.DateTimeField()
    sender = models.ForeignKey('userauth.CustomUser', null = True, on_delete = models.SET_NULL)
    text = models.CharField(max_length = 2000)
    reply_to = models.ForeignKey('messaging.Message', null=True, on_delete = models.SET_NULL)
    snippet = models.CharField(max_length = 200, default = 'messaging/user_message_snippet.html')
    chat = models.ForeignKey('messaging.Chat', on_delete = models.CASCADE)

class Chat(models.Model):
    uuid = models.UUIDField(default = uuid4, editable = False)
