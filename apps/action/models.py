# pyre-strict

from django.db import models
from uuid import uuid4

class Action(models.Model):
    uuid = models.UUIDField(defualt=uuid4)
    creator = models.ForeignKey('userauth.CustomUser', on_delete = models.CASCADE)
    receiver = models.ForeignKey('userauth.CustomUser', on_delete = models.CASCADE)
    kind = models.CharField # TODO: this should have constraints on what it can be
