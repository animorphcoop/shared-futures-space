# pyre-strict

from django.core.exceptions import ValidationError
from django.db import models
from uuid import uuid4
import re

def validate_postcode(postcode):
    if not re.match(r'[a-zA-Z]{1,2}[0-9][a-zA-0-9]?\s?[0-9][a-zA-Z]{2}', postcode):
        raise ValidationError('not a valid uk postcode: %(value)s', params = {'value': postcode})

class Area(models.Model):
    uuid: models.UUIDField = models.UUIDField(default=uuid4, editable=False)
    name: models.CharField = models.CharField(max_length = 50)

class PostCode(models.Model):
    code: models.CharField = models.CharField(max_length = 8, validators = [validate_postcode])
    area: models.ForeignKey = models.ForeignKey(Area, on_delete = models.CASCADE, null = True)
    def save(self, *args, **kwargs):
        # normalise different ways of writing the postcode
        print(self.code)
        m = re.match(r'([a-zA-Z]{1,2}[0-9][a-zA-Z0-9]?)\s?([0-9][a-zA-Z]{2})', self.code)
        self.code = m.group(1).upper() + ' ' + m.group(2).upper()
        super().save(*args, **kwargs)
