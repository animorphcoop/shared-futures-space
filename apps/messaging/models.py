# pyre-strict

from django.utils import timezone
from django.db import models
from uuid import uuid4

class Message(models.Model):
    uuid = models.UUIDField(default = uuid4, editable = False)
    timestamp = models.DateTimeField(default=timezone.now)
    sender = models.ForeignKey('userauth.CustomUser', null = True, on_delete = models.SET_NULL)
    text = models.CharField(max_length = 2000, default = '')
    snippet = models.CharField(max_length = 2000, default = '')
    reply_to = models.ForeignKey('messaging.Message', null=True, on_delete = models.SET_NULL)
    chat = models.ForeignKey('messaging.Chat', on_delete = models.CASCADE)
    # context_* values are nullable fields used to fill in the gaps in system messages
    context_action = models.ForeignKey('action.Action', null = True, on_delete = models.SET_NULL)
    context_project = models.ForeignKey('project.Project', null = True, on_delete = models.SET_NULL)
    context_user_a = models.ForeignKey('userauth.CustomUser', null = True, on_delete = models.SET_NULL, related_name = 'user_a')
    context_user_b = models.ForeignKey('userauth.CustomUser', null = True, on_delete = models.SET_NULL, related_name = 'user_b')
    context_bool = models.BooleanField(default=False)

class Chat(models.Model):
    uuid = models.UUIDField(default = uuid4, editable = False)
