import json

from allauth.account.admin import EmailAddress
from area.models import Area, PostCode
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from userauth.models import CustomUser, Organisation, UserAvatar

DATA_DIR = "dev/autoupload/"


def add_organisations(data):
    for org_data in data:
        try:
            Organisation.objects.get_or_create(
                name=org_data["name"], link=org_data["link"]
            )
        except Exception as e:
            print(
                "could not add organisation with definition: "
                + str(org_data)
                + "\nerror given: "
                + repr(e)
            )


def add_users(users_data):
    for user_data in users_data:
        try:
            new_user = CustomUser.objects.get_or_create(
                display_name=user_data["display name"],
                email=user_data["email"],
                year_of_birth=user_data["year of birth"],
                post_code=PostCode.objects.get_or_create(code=user_data["postcode"])[0],
                avatar=UserAvatar.objects.get_or_create(pk=user_data["avatar"])[0],
                editor=user_data["editor"],
                organisation=Organisation.objects.get_or_create(
                    name=user_data["organisation"]
                )[0]
                if "organisation" in user_data
                else None,
                added_data=True,
                username=user_data["display name"],
            )[0]
            new_user.set_password(user_data["password"])
            new_user.save()
            eml = EmailAddress.objects.get_or_create(
                email=user_data["email"], verified=True, primary=True, user=new_user
            )[0]
            eml.save()
        except Exception as e:
            print(
                "could not add user with definition: "
                + str(user_data)
                + "\nerror given: "
                + repr(e)
            )


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
    help = "import development data"

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
        add_organisations(data["Organisations"])
        add_users(data["Users"])
