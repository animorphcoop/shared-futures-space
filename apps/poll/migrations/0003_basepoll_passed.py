# Generated by Django 4.0.6 on 2022-12-13 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='basepoll',
            name='passed',
            field=models.BooleanField(default=False),
        ),
    ]