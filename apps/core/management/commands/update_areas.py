import json

from django.core.management import BaseCommand

from core.management.commands.loaddevdata import add_areas


class Command(BaseCommand):
    help = "update areas"

    def add_arguments(self, parser):
        parser.add_argument("datafile", nargs="?", type=str)

    def handle(self, *args, **options):
        with open(options["datafile"]) as f:
            data = json.load(f)
            add_areas(data["Areas"])
