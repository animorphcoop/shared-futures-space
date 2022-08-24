from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from apps.core.helpers.slugifier import generate_random_string

from .models import Resource

#TODO: might be an issue that Resource is sending
@receiver(pre_save, sender=Resource)
def add_slug_to_question(sender, instance, *args, **kwargs):
    if instance and not instance.slug:
        slug = slugify(instance.title)
        random_string = generate_random_string()
        instance.slug = slug + "-" + random_string
