import json
from io import BytesIO
import os

from allauth.account.admin import EmailAddress
from area.models import Area, PostCode
from django.contrib.gis.geos import Point
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from PIL import Image as PillowImage
from resources.models import CaseStudy, HowTo
from userauth.models import CustomUser, Organisation, UserAvatar
from wagtail.images.models import Image
from wagtail.rich_text import RichText
from django.contrib.contenttypes.models import ContentType
from taggit.models import Tag

DATA_DIR = "dev/autoupload/"

def get_or_create_tag(tag_name):
    """Get or create a Tag, ensuring uniqueness and handling duplicates gracefully."""


    tag, created = Tag.objects.get_or_create(name=tag_name)
    return tag

def add_resources(resource_data):
    for new_howto_data in resource_data["How To"]:
        try:
            # Ensure mandatory fields are not None
            if any(key not in new_howto_data or new_howto_data[key] is None for key in ["title", "summary", "link"]):
                raise ValueError(f"Missing mandatory field for How To: {new_howto_data}")

            # Check if HowTo already exists
            try:
                new_howto = HowTo.objects.get(title=new_howto_data["title"])
                is_new = False
            except HowTo.DoesNotExist:
                is_new = True
                new_howto = HowTo(
                    title=new_howto_data["title"],
                    summary=new_howto_data["summary"],
                    link=new_howto_data["link"],
                    location=new_howto_data.get("location", None),
                    location_exact=new_howto_data.get("location_exact", True),
                )

            new_howto.save()

            # Handle tags
            new_howto.tags.clear()  # Clear existing tags
            for tag_name in new_howto_data.get("tags", []):  # Ensure 'tags' is an empty list if missing
                tag = get_or_create_tag(tag_name)
                new_howto.tags.add(tag)

            new_howto.save()

        except Exception as e:
            print(
                f"Error loading How To '{new_howto_data.get('title', 'Unknown')}': {e}"
            )

    for new_casestudy_data in resource_data["Case Study"]:
        try:
            # Ensure mandatory fields are not None
            if any(key not in new_casestudy_data or new_casestudy_data[key] is None for key in
                   ["title", "summary", "link", "body"]):
                raise ValueError(f"Missing mandatory field for case study: {new_casestudy_data}")

            # Check if case study already exists
            try:
                new_casestudy = CaseStudy.objects.get(title=new_casestudy_data["title"])
                is_new = False
            except CaseStudy.DoesNotExist:
                is_new = True
                new_casestudy = CaseStudy(
                    title=new_casestudy_data["title"],
                    summary=new_casestudy_data["summary"],
                    link=new_casestudy_data["link"],
                    location=new_casestudy_data.get("location", None),
                    location_exact=new_casestudy_data.get("location_exact", True),
                )

            # Handle image
            if new_casestudy_data["image"]:
                with open(os.path.join(DATA_DIR, new_casestudy_data["image"]), "rb") as f:
                    img = Image.objects.get_or_create(
                        file=ImageFile(BytesIO(f.read()), name=new_casestudy_data["image"])
                    )[0]
                new_casestudy.case_study_image = img
            elif is_new:
                new_casestudy.case_study_image = None

            if new_casestudy_data["body"]:
                new_casestudy.body = [("body_text", {"content": RichText(new_casestudy_data["body"])})]

            new_casestudy.save()

            # Handle tags
            new_casestudy.tags.clear()  # Clear existing tags
            for tag_name in new_casestudy_data.get("tags", []):  # Ensure 'tags' is an empty list if missing
                tag = get_or_create_tag(tag_name)
                new_casestudy.tags.add(tag)

            new_casestudy.save()

        except Exception as e:
            print(
                f"Error loading case study '{new_casestudy_data.get('title', 'Unknown')}': {e}"
            )


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


def add_avatars(avatars_data):
    for avatar_data in avatars_data:
        try:
            with open(DATA_DIR + avatar_data["avatar"], "rb") as f:
                new_avatar = UserAvatar.objects.create()
                new_avatar.avatar = ImageFile(f)
                new_avatar.save()
        except Exception as e:
            print(
                "could not add avatar with definition: "
                + str(avatar_data)
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

        add_avatars(data["User Avatars"])
        if options["datafile"] == "autoupload/avatars.json":
            # if datafile is avatars only, exit with success,
            # else continue with the rest
            exit(0)
        add_areas(data["Areas"])
        add_resources(data["Resources"])
        add_organisations(data["Organisations"])
        add_users(data["Users"])