# Generated by Django 4.2.3 on 2024-02-19 15:39

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("area", "0002_area_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="area",
            name="location",
            field=django.contrib.gis.db.models.fields.PointField(
                geography=True, null=True, srid=4326
            ),
        ),
    ]
