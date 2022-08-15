from django.db import models
from wagtail.snippets.models import register_snippet

from project.models import Project # pyre-ignore[21]
from resources.models import Resource # pyre-ignore[21]
from uuid import uuid4



@register_snippet
class Tag(models.Model):
    uuid: models.UUIDField = models.UUIDField(
        default = uuid4, editable = False
    )

    name : models.CharField = models.CharField(
        max_length=50,
        blank=False,
        null=False,
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        # template = "resources/resources.html"
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

class ProjectTag(models.Model):
    project: models.ForeignKey = models.ForeignKey(Project, on_delete = models.CASCADE)
    tag: models.ForeignKey = models.ForeignKey(Tag, on_delete = models.CASCADE)

class ResourceTag(models.Model):
    resource: models.ForeignKey = models.ForeignKey(Resource, on_delete = models.CASCADE)
    tag: models.ForeignKey = models.ForeignKey(Tag, on_delete = models.CASCADE)
