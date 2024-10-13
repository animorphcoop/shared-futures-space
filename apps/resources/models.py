import json
from typing import Optional
from uuid import uuid4

from core.utils.tags_declusterer import tag_cluster_to_list

from django.contrib.gis.db.models import PointField
from django.core.exceptions import ValidationError

from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import Tag as TaggitTag, TaggedItemBase
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtailgeowidget.panels import LeafletPanel

from apps.core.utils.slugifier import generate_random_string
from apps.streams import blocks

class CustomTag(TaggitTag):
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def save(self, *args, **kwargs):
        if not self.pk and CustomTag.objects.filter(name__iexact=self.name).exists():
            return CustomTag.objects.get(name__iexact=self.name)
        super().save(*args, **kwargs)


class ResourceTag(TaggedItemBase):
    content_object = ParentalKey(
        "resources.Resource", on_delete=models.CASCADE, related_name="tagged_items"
    )
    tag = models.ForeignKey(CustomTag, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s_items")

    class Meta:
        unique_together = ("content_object", "tag")

class SavedResource(models.Model):
    saved_resource = models.ForeignKey(
        "resources.Resource", on_delete=models.CASCADE
    )
    saved_by = models.ForeignKey(
        "userauth.CustomUser", on_delete=models.CASCADE
    )

    @property
    def relevant_to(self) -> Optional[str]:
        if self.saved_by and hasattr(self.saved_by, "pk"):
            return self.saved_by.pk

class Resource(ClusterableModel):
    uuid = models.UUIDField(default=uuid4, editable=False)
    published_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=100, unique=True, editable=False)
    title = models.CharField(max_length=50, blank=False, null=False)
    summary = models.CharField(max_length=300, blank=False, null=False)
    location = PointField(geography=True, srid=4326, blank=True, null=True)
    location_exact = models.BooleanField(default=True)
    link = models.CharField(max_length=200, blank=True, null=True)
    tags = ClusterTaggableManager(through=ResourceTag, blank=True)

    @property
    def tag_list(self):
        if not hasattr(self.tags, "all"):
            return self.tags
        return tag_cluster_to_list(self.tags)

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title + '-' + str(uuid4())[:8])
        super(Resource, self).save(*args, **kwargs)  # Call the actual save method

        unique_tags = {}
        for tag in self.tags.all():
            if tag.name not in unique_tags:
                unique_tags[tag.name] = tag
            else:
                # Avoid dupes by removing duplicates from Resource
                self.tags.remove(tag)


@receiver(pre_save, sender=Resource)
def handle_pre_save(sender, instance, *args, **kwargs):
    unique_tags = {}
    for tag in instance.tags.all():
        if tag.name not in unique_tags:
            unique_tags[tag.name] = tag
        else:
            instance.tags.remove(tag)

class HowTo(Resource):
    class Meta:
        verbose_name = "How To"
        verbose_name_plural = "How Tos"

    panels = [
        FieldPanel("title"),
        FieldPanel("summary"),
        FieldPanel("link"),
        FieldPanel("tags"),
        LeafletPanel("location"),
    ]

class CaseStudy(Resource):
    case_study_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=False,
        max_length=200,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    body = StreamField(
        [("body_text", blocks.RichTextSimpleBlock())],
        null=True,
        blank=True,
        use_json_field=True,
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("summary"),
        FieldPanel("link"),
        FieldPanel("tags"),
        FieldPanel("case_study_image"),
        FieldPanel("location_exact"),
        LeafletPanel("location"),
    ]

    class Meta:
        verbose_name = "Case Study"
        verbose_name_plural = "Case Studies"


@receiver(pre_save, sender=Resource)
def handle_pre_save(sender, instance, *args, **kwargs):
    unique_tags = {}
    for tag in instance.tags.all():
        if tag.name not in unique_tags:
            unique_tags[tag.name] = tag
        else:
            instance.tags.remove(tag)

@receiver(post_save, sender=HowTo)
def add_slug_to_how_to(sender, instance, *args, **kwargs):
    if instance and not instance.slug:
        slug = slugify(instance.title)
        random_string = generate_random_string()
        instance.slug = slug + "-" + random_string
        instance.save()

@receiver(post_save, sender=CaseStudy)
def add_slug_to_case_study(sender, instance, *args, **kwargs):
    if instance and not instance.slug:
        slug = slugify(instance.title)
        random_string = generate_random_string()
        instance.slug = slug + "-" + random_string
        instance.save()