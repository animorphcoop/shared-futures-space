from django.db import models
from apps.streams import blocks
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import StreamFieldPanel




class CaseStudy(models.Model):

    title = models.TextField(
        max_length=500,
        blank=False,
        null=False,
    )
    summary = models.TextField(
        max_length=300,
        blank=False,
        null=False,
    )
    case_study_image = models.ForeignKey(
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


    class Meta:
        verbose_name = "Case Study"
        verbose_name_plural = "Case Studies"
