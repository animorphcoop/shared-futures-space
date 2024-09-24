import json

from area.models import Area, PostCode
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

DATA_DIR = "dev/autoupload/"


def add_areas(areas_data):
    for area_name in areas_data:
        try:
            area_data = areas_data[area_name]
            this_area = Area.objects.get_or_create(name=area_name)[0]
            location = area_data.get("location", None)
            if location:
                this_area.location = Point(
                    float(location["lng"]), float(location["lat"])
                )
            zoom = area_data.get("zoom", None)
            if zoom:
                this_area.zoom = zoom
            for postcode in area_data["postcodes"]:
                PostCode.objects.get_or_create(code=postcode, area=this_area)
            this_area.save()
        except Exception as e:
            print(
                "could not add area with definition: "
                + str(areas_data[area_name])
                + "\nerror given: "
                + repr(e)
            )


class Command(BaseCommand):
    help = "import area data"

    def add_arguments(self, parser):
        parser.add_argument("datafile", nargs="?", type=str)

    def handle(self, *args, **options):
        try:
            f = open(options["datafile"])
            try:
                data = json.load(f)
            except:
                print("could not parse valid json from " + options["datafile"])
                exit()
            f.close()
        except:
            print("could not read from file: " + options["datafile"])
            exit()

        add_areas(data["Areas"])
