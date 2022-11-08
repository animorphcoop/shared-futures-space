# pyre-strict

from django.db import models
from modelcluster.models import ClusterableModel

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from apps.streams import blocks
from uuid import uuid4

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from apps.core.utils.slugifier import generate_random_string
from typing import Optional


class ResourceTag(TaggedItemBase):
    content_object = ParentalKey('resources.Resource', on_delete=models.CASCADE, related_name='tagged_items')


class SavedResource(models.Model):
    saved_resource: models.ForeignKey = models.ForeignKey('resources.Resource',
                                                          on_delete=models.CASCADE)
    saved_by: models.ForeignKey = models.ForeignKey('userauth.CustomUser', on_delete=models.CASCADE)

    @property
    def relevant_to(self) -> Optional[str]:
        if self.saved_by and hasattr(self.saved_by, 'pk'):
            return self.saved_by.pk




# do not create Resources! this model is just to inherit specific kinds of resources from
# you can however query Resource.objects, and django will automatically search for anything that inherits from this model. that's pretty neat!
class Resource(ClusterableModel):
    uuid: models.UUIDField = models.UUIDField(
        default=uuid4, editable=False
    )
    published_on: models.DateTimeField = models.DateTimeField(
        auto_now_add=True
    )
    edited_on: models.DateTimeField = models.DateTimeField(
        auto_now=True
    )
    slug: models.SlugField = models.SlugField(
        max_length=100,
        unique=True,
        editable=False
    )
    title: models.CharField = models.CharField(
        max_length=50,
        blank=False,
        null=False,
    )
    summary: models.CharField = models.CharField(
        max_length=300,
        blank=False,
        null=False,
    )
    link: models.CharField = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )
    tags = ClusterTaggableManager(through=ResourceTag, blank=True)

    def __str__(self) -> str:
        return f"{self.title}"


class HowTo(Resource):
    class Meta:
        verbose_name = 'How To'
        verbose_name_plural = 'How Tos'


class CaseStudy(Resource):
    case_study_image: models.ForeignKey = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=False,
        max_length=200,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    # could be a streamfield
    body = StreamField([
        ("body_text", blocks.RichTextSimpleBlock()),
    ], null=True, blank=True, use_json_field=True)

    content_panels = [
        FieldPanel("body"),
    ]

    class Meta:
        verbose_name = 'Case Study'
        verbose_name_plural = 'Case Studies'


# SIGNALS
# TODO: Find out 'sender' type
@receiver(post_save, sender=HowTo)
def add_slug_to_how_to(sender, instance, *args, **kwargs) -> None:  # pyre-ignore[2]
    if instance and not instance.slug:
        slug = slugify(instance.title)
        random_string = generate_random_string()
        instance.slug = slug + "-" + random_string
        instance.save()


@receiver(post_save, sender=CaseStudy)
def add_slug_to_case_study(sender, instance, *args, **kwargs) -> None:  # pyre-ignore[2]
    if instance and not instance.slug:
        slug = slugify(instance.title)
        random_string = generate_random_string()
        instance.slug = slug + "-" + random_string
        instance.save()
