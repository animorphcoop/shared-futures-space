from uuid import uuid4

from django.db import models

from userauth.models import CustomUser


class Task(models.Model):
    uuid: models.UUIDField = models.UUIDField(default=uuid4, editable=False)
    name: models.CharField = models.CharField(max_length=120)
    done: models.BooleanField = models.BooleanField(default=False)
    due: models.DateTimeField = models.DateTimeField(null=True)
    responsible: models.ForeignKey = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
