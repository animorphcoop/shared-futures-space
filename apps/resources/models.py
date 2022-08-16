from django.db import models
from wagtail.snippets.models import register_snippet

from tags.models import Tag, ResourceTag # pyre-ignore[21]

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

    tags: models.TextField = models.TextField(
        # purely for the wagtail form
        # overriden 'save()' takes the data, uses it and removes it
        max_length=150,
        blank=True,
        null=False
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) # do this first because can't save the resourcetags that reference it until it itself is saved
        tagnames = map(str.strip, self.tags.split(','))
        ResourceTag.objects.filter(resource=self).delete()
        for name in tagnames:
            try:
                target_tag = Tag.objects.get(name=name)
            except Tag.DoesNotExist:
                target_tag = Tag.objects.create(name=name)
            ResourceTag.objects.create(tag=target_tag, resource=self)


    def __str__(self):
        return f"{self.title}"

    class Meta:
        #app_label = 'IDIOT'
        verbose_name = "Resource"
        #verbose_name_plural = "Resources"

