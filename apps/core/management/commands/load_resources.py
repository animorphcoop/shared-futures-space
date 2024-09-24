import json
from io import BytesIO

from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from PIL import Image as PillowImage
from resources.models import CaseStudy, HowTo
from taggit.models import Tag
from wagtail.images.models import Image
from wagtail.rich_text import RichText

DATA_DIR = "dev/autoupload/"


def add_resources(resource_data):
    for new_howto_data in resource_data["How To"]:
        try:
            new_howto = HowTo.objects.get_or_create(
                title=new_howto_data["title"],
                summary=new_howto_data["summary"],
                link=new_howto_data["link"],
                location=new_howto_data.get("location", None),
                location_exact=new_howto_data.get("location_exact", True),
            )[0]
            for tag_name in new_howto_data["tags"]:
                tag, created = Tag.objects.get_or_create(name=tag_name)
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
                        location=new_casestudy_data.get("location", None),
                        location_exact=new_casestudy_data.get("location_exact", True),
                    )[0]
                    new_casestudy.body.append(
                        ("body_text", {"content": RichText(new_casestudy_data["body"])})
                    )

                    for tag_name in new_casestudy_data["tags"]:
                        tag, created = Tag.objects.get_or_create(name=tag_name)
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
                location=new_casestudy_data.get("location", None),
                location_exact=new_casestudy_data.get("location_exact", True),
            )[0]
            new_casestudy.body.append(
                ("body_text", {"content": RichText(new_casestudy_data["body"])})
            )

            for tag_name in new_casestudy_data["tags"]:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                new_casestudy.tags.add(tag)
            new_casestudy.save()


class Command(BaseCommand):
    help = "import resource data"

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

        add_resources(data["Resources"])
