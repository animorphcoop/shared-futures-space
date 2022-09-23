# pyre-strict

from django.core.exceptions import ValidationError
from django.db import models
from uuid import uuid4
import re

from typing import Any, Dict, List, Tuple


def validate_postcode(postcode: str) -> None:
    if not re.match(r'[a-zA-Z]{1,2}[0-9][a-zA-0-9]?\s?([0-9][a-zA-Z]{2})?', postcode):
        raise ValidationError('not a valid UK postcode: %(value)s', params = {'value': postcode})


class Area(models.Model):
    uuid: models.UUIDField = models.UUIDField(default=uuid4, editable=False)
    name: models.CharField = models.CharField(max_length = 50)
    def __str__(self) -> str:
        return self.name


# Post Codes will be automatically added, if one does not exist, it can belong to 'other' area
class PostCode(models.Model):
    code: models.CharField = models.CharField(max_length = 4)
    area: models.ForeignKey = models.ForeignKey(Area, on_delete = models.CASCADE, null = True)
    def save(self, *args: Tuple[Any], **kwargs: Dict[str,Any]) -> None:
        # normalise different ways of writing the postcode - TODO: carrying cleaning on the frontend & view
        m = re.match(r'([a-zA-Z]{1,2}[0-9][a-zA-Z0-9]?)\s?([0-9][a-zA-Z]{2})?', self.code)
        self.code = m.group(1).upper() # discard second part
        if not self.area:
            self.area = Area.objects.get_or_create(name='Other')[0]
        return super().save(*args, **kwargs) # pyre-ignore[6]

    def __str__(self) -> str:
        return self.code

