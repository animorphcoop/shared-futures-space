from django.core.management.base import BaseCommand
from django.db import models
from taggit.models import Tag
from resources.models import HowTo, CaseStudy


class Command(BaseCommand):
    help = 'Remove duplicate tags from the database'

    def handle(self, *args, **kwargs):
        duplicate_tags = Tag.objects.values('name').annotate(name_count=models.Count('name')).filter(name_count__gt=1)

        for tag in duplicate_tags:
            duplicate_instances = Tag.objects.filter(name=tag['name']).order_by('id')
            primary_tag = duplicate_instances.first()

            for duplicate in duplicate_instances[1:]:
                for resource in HowTo.objects.filter(tags=duplicate):
                    resource.tags.remove(duplicate)
                    resource.tags.add(primary_tag)

                for resource in CaseStudy.objects.filter(tags=duplicate):
                    resource.tags.remove(duplicate)
                    resource.tags.add(primary_tag)

                duplicate.delete()

        self.stdout.write(self.style.SUCCESS('Duplicate tags merged successfully.'))
