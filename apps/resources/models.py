# pyre-strict

from django.db import models
from modelcluster.models import ClusterableModel

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from uuid import uuid4

class ResourceTag(TaggedItemBase):
    content_object = ParentalKey('resources.Resource', on_delete=models.CASCADE, related_name='tagged_items')

class Resource(ClusterableModel):
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

    tags = ClusterTaggableManager(through=ResourceTag, blank=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        #app_label = 'IDIOT'
        verbose_name = "Resource"
        #verbose_name_plural = "Resources"

