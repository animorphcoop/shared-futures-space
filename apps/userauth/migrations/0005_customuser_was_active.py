# Generated by Django 4.0.6 on 2023-07-11 11:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("userauth", "0004_customuser_postcode_changes"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="was_active",
            field=models.BooleanField(default=True),
        ),
    ]