# pyre-strict

from django.utils import timezone
from django.db import models
from uuid import uuid4

class Message(models.Model):
    uuid: models.UUIDField = models.UUIDField(default = uuid4, editable = False)
    timestamp: models.DateTimeField = models.DateTimeField(default=timezone.now)
    sender: models.ForeignKey = models.ForeignKey('userauth.CustomUser', null = True, on_delete = models.SET_NULL)
    text: models.CharField = models.CharField(max_length = 2000, default = '')
    image: models.ImageField = models.ImageField(upload_to='messages/images/', blank=True)
    file: models.FileField = models.FileField(upload_to='messages/files/', blank=True)
    snippet: models.CharField = models.CharField(max_length = 2000, default = '')
    reply_to: models.ForeignKey = models.ForeignKey('messaging.Message', null=True, on_delete = models.SET_NULL)
    chat: models.ForeignKey = models.ForeignKey('messaging.Chat', on_delete = models.CASCADE)
    # context_* values are nullable fields used to fill in the gaps in system messages
    context_action: models.ForeignKey = models.ForeignKey('action.Action', null = True, on_delete = models.SET_NULL)
    context_project: models.ForeignKey = models.ForeignKey('project.Project', null = True, on_delete = models.SET_NULL)
    context_user_a: models.ForeignKey = models.ForeignKey('userauth.CustomUser', null = True, on_delete = models.SET_NULL, related_name = 'user_a')
    context_user_b: models.ForeignKey = models.ForeignKey('userauth.CustomUser', null = True, on_delete = models.SET_NULL, related_name = 'user_b')
    context_bool: models.BooleanField = models.BooleanField(default=False)
    context_poll: models.ForeignKey = models.ForeignKey('poll.Poll', null = True, on_delete = models.SET_NULL)

class Chat(models.Model):
    uuid: models.UUIDField = models.UUIDField(default = uuid4, editable = False)
