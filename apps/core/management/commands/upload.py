from django.core.management.base import BaseCommand, CommandError

from resources.models import Resource

data = {'Resources': [{'title': 'test resource 1', 'content': 'this resource helps you to do something', 'tags': ['resource', 'useful']},
                      {'title': 'test resource 2', 'content': 'this resource points you to an external project', 'tags': ['resource', 'organisation']}]}

class Command(BaseCommand):
    help = 'import data'

    def add_arguments(self, parser):
        parser.add_argument('n', nargs='?', type=int, default=0)

    def handle(self, *args, **options):
        for new_resource_data in data['Resources']:
            print(new_resource_data)
            new_resource = Resource.objects.create(title=new_resource_data['title'], content=new_resource_data['content'])
            for tag in new_resource_data['tags']:
                new_resource.tags.add(tag)
            new_resource.save()
