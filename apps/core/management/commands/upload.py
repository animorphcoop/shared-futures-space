from django.core.management.base import BaseCommand, CommandError

data = {'Resources': [{}]}

class Command(BaseCommand):
    help = 'import data'

    def add_arguments(self, parser):
        parser.add_argument('n', nargs='?', type=int, default=0)

    def handle(self, *args, **options):
        print(options['n'])
