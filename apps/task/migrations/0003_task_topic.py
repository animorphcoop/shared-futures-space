# Generated by Django 4.0.6 on 2023-09-13 16:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("task", "0002_task_river_task_stage_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="topic",
            field=models.CharField(default="", max_length=32),
            preserve_default=False,
        ),
    ]