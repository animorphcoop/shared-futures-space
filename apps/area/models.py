# pyre-strict

from django.db import models
from uuid import uuid4


def Area(models.Model):
    uuid: models.UUIDField = models.UUIDField(default=uuid4, editable=False)
    name: models.CharField = models.CharField(max_length = 50)

def PostCode(models.Model):
    code: models.CharField = models.CharField(max_length = 8)
    area: models.ForeignKey = models.ForeignKey(Area, on_delete = models.CASCADE)
