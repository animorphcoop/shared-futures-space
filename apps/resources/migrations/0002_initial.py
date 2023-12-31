# Generated by Django 4.0.6 on 2022-11-09 16:41

import django.db.models.deletion
import modelcluster.contrib.taggit
import modelcluster.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("taggit", "0004_alter_taggeditem_content_type_alter_taggeditem_tag"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("resources", "0001_initial"),
        ("wagtailimages", "0024_index_image_file_hash"),
    ]

    operations = [
        migrations.AddField(
            model_name="savedresource",
            name="saved_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="savedresource",
            name="saved_resource",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="resources.resource"
            ),
        ),
        migrations.AddField(
            model_name="resourcetag",
            name="content_object",
            field=modelcluster.fields.ParentalKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tagged_items",
                to="resources.resource",
            ),
        ),
        migrations.AddField(
            model_name="resourcetag",
            name="tag",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(app_label)s_%(class)s_items",
                to="taggit.tag",
            ),
        ),
        migrations.AddField(
            model_name="resource",
            name="tags",
            field=modelcluster.contrib.taggit.ClusterTaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="resources.ResourceTag",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
        migrations.AddField(
            model_name="casestudy",
            name="case_study_image",
            field=models.ForeignKey(
                max_length=200,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
    ]
