from django.db import models
from wagtail.snippets.models import register_snippet

from uuid import uuid4

class Resource(models.Model):
    uuid: models.UUIDField = models.UUIDField(
        default = uuid4, editable = False
    )

    title : models.CharField = models.CharField(
        max_length=50,
        blank=False,
        null=False,
    )

    content : models.TextField = models.TextField(
        max_length=500,
        blank=False,
        null=False,
    )

    def __str__(self):
        return f"{self.title}"

    class Meta:
        #app_label = 'IDIOT'
        verbose_name = "Resource"
        #verbose_name_plural = "Resources"

