# Generated by Django 4.2.3 on 2024-02-15 14:38

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("resources", "0003_alter_resource_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="resource",
            name="location",
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True, geography=True, null=True, srid=4326
            ),
        ),
    ]
