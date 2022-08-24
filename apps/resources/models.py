# pyre-strict

from django.db import models
from modelcluster.models import ClusterableModel

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.fields import StreamField
from wagtail.admin.panels import StreamFieldPanel
from apps.streams import blocks
from uuid import uuid4

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from apps.core.helpers.slugifier import generate_random_string

# you need to specify each model's tag system seperately because the db doesn't have a notion of inheritance
# thy still autocomplete tags that were defined on other models though
class HowToTag(TaggedItemBase):
    content_object = ParentalKey('resources.HowTo', on_delete=models.CASCADE, related_name='tagged_items')


class CaseStudyTag(TaggedItemBase):
    content_object = ParentalKey('resources.CaseStudy', on_delete=models.CASCADE, related_name='tagged_items')


# do not create Resources! this model is just to inherit specific kinds of resources from
class Resource(ClusterableModel):
    uuid: models.UUIDField = models.UUIDField(
        default=uuid4, editable=False
    )
    published_on: models.DateTimeField = models.DateTimeField(
        auto_now_add=True
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
        max_length=50,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.title}"


class HowTo(Resource):
    tags = ClusterTaggableManager(through=HowToTag, blank=True)

    class Meta:
        verbose_name = 'How To'
        verbose_name_plural = 'How Tos'


class CaseStudy(Resource):
    case_study_image: models.ForeignKey = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    # could be a streamfield
    body = StreamField([
        ("body_text", blocks.RichTextSimpleBlock()),
    ], null=True, blank=True)

    content_panels = [
        StreamFieldPanel("body"),
    ]

    tags = ClusterTaggableManager(through=CaseStudyTag, blank=True)

    class Meta:
        verbose_name = 'Case Study'
        verbose_name_plural = 'Case Studies'



# SIGNALS
@receiver(post_save, sender=HowTo)
def add_slug_to_how_to(sender, instance, *args, **kwargs):
    print('received signal from HowTo')
    if instance and not instance.slug:
        slug = slugify(instance.title)
        random_string = generate_random_string()
        instance.slug = slug + "-" + random_string
        print('about to save slug HowTo')
        instance.save()


@receiver(post_save, sender=CaseStudy)
def add_slug_to_case_study(sender, instance, *args, **kwargs):
    print('received signal from CaseStudy')
    if instance and not instance.slug:
        slug = slugify(instance.title)
        random_string = generate_random_string()
        instance.slug = slug + "-" + random_string
        print('about to save slug CaseStudy')
        instance.save()