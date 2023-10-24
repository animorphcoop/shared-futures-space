import json
from io import BytesIO

from allauth.account.admin import EmailAddress
from area.models import Area, PostCode
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from messaging.models import Message
from PIL import Image as PillowImage
from poll.models import SingleChoicePoll, SingleVote
from resources.models import CaseStudy, HowTo
from river.models import River, RiverMembership
from userauth.models import CustomUser, Organisation, UserAvatar
from userauth.util import get_userpair
from wagtail.images.models import Image
from wagtail.rich_text import RichText

DATA_DIR = "devdata/"


def add_resources(resource_data):
    for new_howto_data in resource_data["How To"]:
        try:
            new_howto = HowTo.objects.get_or_create(
                title=new_howto_data["title"],
                summary=new_howto_data["summary"],
                link=new_howto_data["link"],
            )[0]
            for tag in new_howto_data["tags"]:
                new_howto.tags.add(tag)
            new_howto.save()
        except Exception as e:
            print(
                "could not add howto with definition: "
                + str(new_howto_data)
                + "\nerror given: "
                + repr(e)
            )
    for new_casestudy_data in resource_data["Case Study"]:
        if new_casestudy_data["image"] != "":
            try:
                with open(DATA_DIR + new_casestudy_data["image"], "rb") as f:
                    pimg = PillowImage.open(DATA_DIR + new_casestudy_data["image"])
                    img = Image.objects.get_or_create(
                        file=ImageFile(
                            BytesIO(f.read()), name=new_casestudy_data["image"]
                        ),
                        width=pimg.width,
                        height=pimg.height,
                    )[0]
                    new_casestudy = CaseStudy.objects.get_or_create(
                        title=new_casestudy_data["title"],
                        summary=new_casestudy_data["summary"],
                        case_study_image=img,
                        link=new_casestudy_data["link"],
                    )[0]
                    new_casestudy.body.append(
                        ("body_text", {"content": RichText(new_casestudy_data["body"])})
                    )

                    for tag in new_casestudy_data["tags"]:
                        new_casestudy.tags.add(tag)
                    new_casestudy.save()

            except Exception as e:
                print(
                    "could not load case study image: "
                    + str(new_casestudy_data["title"])
                    + "\nerror given: "
                    + repr(e)
                )
        else:
            print(str(new_casestudy_data["title"]) + " has no image")
            new_casestudy = CaseStudy.objects.get_or_create(
                title=new_casestudy_data["title"],
                summary=new_casestudy_data["summary"],
                link=new_casestudy_data["link"],
            )[0]
            new_casestudy.body.append(
                ("body_text", {"content": RichText(new_casestudy_data["body"])})
            )

            for tag in new_casestudy_data["tags"]:
                new_casestudy.tags.add(tag)
            new_casestudy.save()

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
            this_area = Area.objects.get_or_create(name=area_name)[0]
            for postcode in areas_data[area_name]:
                PostCode.objects.get_or_create(code=postcode, area=this_area)
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
        if options["datafile"] == "devdata/avatars.json":
            # if datafile is avatars only, exit with success,
            # else continue with the rest
            exit(0)
        add_areas(data["Areas"])
        add_resources(data["Resources"])
        add_organisations(data["Organisations"])
        add_users(data["Users"])
