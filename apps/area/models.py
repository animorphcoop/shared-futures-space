import re
from typing import Any, Dict, Tuple
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models


def validate_postcode(postcode: str) -> None:
    if not re.match(r"[a-zA-Z]{1,2}[0-9][a-zA-0-9]?\s?([0-9][a-zA-Z]{2})?", postcode):
        raise ValidationError(
            "not a valid UK postcode: %(value)s", params={"value": postcode}
        )


# get matching postcode, a straight get_or_create doesn't work because it edits its own .code
def get_postcode(code):
    m = re.match(r"([a-zA-Z]{1,2}[0-9][a-zA-Z0-9]?)\s?([0-9][a-zA-Z]{2})?", code)
    if m is not None:
        return PostCode.objects.get_or_create(code=m.group(1).upper())[0]
    else:
        return PostCode.objects.get_or_create(code=code)[0]


class Area(models.Model):
    uuid: models.UUIDField = models.UUIDField(default=uuid4, editable=False)
    name: models.CharField = models.CharField(max_length=50)
    image: models.ImageField = models.ImageField(
        upload_to="areas/images/", null=True, blank=True
    )

    def __str__(self) -> str:
        return self.name


# Post Codes will be automatically added, if one does not exist, it can belong to 'other' area
class PostCode(models.Model):
    code: models.CharField = models.CharField(max_length=4)
    area: models.ForeignKey = models.ForeignKey(
        Area, on_delete=models.CASCADE, null=True
    )

    def save(self, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> None:
        m = re.match(
            r"([a-zA-Z]{1,2}[0-9][a-zA-Z0-9]?)\s?([0-9][a-zA-Z]{2})?", self.code
        )
        if m is not None:
            self.code = m.group(1).upper()  # discard incode
        if not self.area:
            self.area = Area.objects.get_or_create(name="Other")[0]
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.code
