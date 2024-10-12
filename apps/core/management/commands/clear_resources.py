from django.core.management.base import BaseCommand
from resources.models import CaseStudy, HowTo


class Command(BaseCommand):
    help = 'Clears all HowTo and CaseStudy entries from the database'

    def handle(self, *args, **options):
        HowTo.objects.all().delete()
        CaseStudy.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully cleared HowTo and CaseStudy entries'))
