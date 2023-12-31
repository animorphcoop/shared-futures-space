# Generated by Django 4.2.3 on 2023-07-19 12:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("userauth", "0005_customuser_was_active"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(
                blank=True, max_length=254, unique=True, verbose_name="email address"
            ),
        ),
    ]
