# Generated by Django 4.0.6 on 2023-06-16 11:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="wizard",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
