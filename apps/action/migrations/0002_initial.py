# Generated by Django 4.0.6 on 2022-11-09 16:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('river', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('action', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='action',
            name='param_river',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='river.river'),
        ),
        migrations.AddField(
            model_name='action',
            name='receiver',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to=settings.AUTH_USER_MODEL),
        ),
    ]
