from django.core.management.base import BaseCommand
from resources.models import CaseStudy, HowTo, ResourceTag, CustomTag
from taggit.models import Tag


class Command(BaseCommand):
    help = 'Clears all HowTo and CaseStudy entries from the database'

    def handle(self, *args, **options):
        # clear tags
        ResourceTag.objects.all().delete()
        CustomTag.objects.all().delete()
        Tag.objects.all().delete()

        # remove items
        HowTo.objects.all().delete()
        CaseStudy.objects.all().delete()
        ResourceTag.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully cleared HowTo and CaseStudy entries'))
