# Generated by Django 4.0.6 on 2022-11-09 16:41

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('area', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalyticsSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sessid_hash', models.CharField(max_length=128)),
                ('area', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='area.area')),
            ],
        ),
        migrations.CreateModel(
            name='AnalyticsEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('type', models.CharField(choices=[('SIGNUP', 'signup'), ('LOGIN', 'login'), ('RESOURCE', 'resource')], max_length=8)),
                ('session', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='analytics.analyticssession')),
            ],
        ),
    ]
