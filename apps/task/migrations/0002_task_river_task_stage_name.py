# Generated by Django 4.0.6 on 2023-09-13 11:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("river", "0006_alter_river_current_stage"),
        ("task", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="river",
            # TODO: squash these migrations, no default here...
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="river.river"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="task",
            name="stage_name",
            field=models.CharField(
                choices=[("plan", "Plan"), ("act", "Act")], default="plan", max_length=8
            ),
            preserve_default=False,
        ),
    ]