# Generated by Django 4.0.6 on 2022-11-09 16:41

from django.db import migrations, models
import django.db.models.deletion
import uuid
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('published_on', models.DateTimeField(auto_now_add=True)),
                ('edited_on', models.DateTimeField(auto_now=True)),
                ('slug', models.SlugField(editable=False, max_length=100, unique=True)),
                ('title', models.CharField(max_length=50)),
                ('summary', models.CharField(max_length=300)),
                ('link', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ResourceTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SavedResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='CaseStudy',
            fields=[
                ('resource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.resource')),
                ('body', wagtail.fields.StreamField([('body_text', wagtail.blocks.StructBlock([('content', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'ol', 'ul', 'link']))]))], blank=True, null=True, use_json_field=True)),
            ],
            options={
                'verbose_name': 'Case Study',
                'verbose_name_plural': 'Case Studies',
            },
            bases=('resources.resource',),
        ),
        migrations.CreateModel(
            name='HowTo',
            fields=[
                ('resource_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='resources.resource')),
            ],
            options={
                'verbose_name': 'How To',
                'verbose_name_plural': 'How Tos',
            },
            bases=('resources.resource',),
        ),
    ]
