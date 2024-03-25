import json

from core.management.commands.loaddevdata import add_areas
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "update areas"

    def add_arguments(self, parser):
        parser.add_argument("datafile", nargs="?", type=str)

    def handle(self, *args, **options):
        with open(options["datafile"]) as f:
            data = json.load(f)
            add_areas(data["Areas"])
