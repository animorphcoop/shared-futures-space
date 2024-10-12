import json
from io import BytesIO
import os
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from resources.models import CaseStudy, HowTo, CustomTag
from wagtail.images.models import Image
from wagtail.rich_text import RichText
from django.db import IntegrityError

DATA_DIR = "dev/autoupload/"


class Command(BaseCommand):
    help = 'Adds HowTo and CaseStudy entries from the database'

    def add_arguments(self, parser):
        parser.add_argument('resource_file', type=str, help='Path to the resources JSON file')

    def handle(self, *args, **options):
        resource_file = options['resource_file']
        with open(resource_file, 'r') as file:
            resource_data = json.load(file)
            self.add_resources(resource_data)

    def get_or_create_custom_tag(self, tag_name):
        """Get or create a CustomTag, handling any integrity errors."""
        tag_name_lower = tag_name.lower()
        try:
            tag, created = CustomTag.objects.get_or_create(name__iexact=tag_name_lower, defaults={"name": tag_name})
            if created:
                self.stdout.write(self.style.SUCCESS(f"Tag created: {tag_name}"))
        except IntegrityError:
            tag = CustomTag.objects.get(name__iexact=tag_name_lower)
            self.stdout.write(self.style.WARNING(f"Tag fetched due to IntegrityError: {tag_name}"))
        return tag

    def add_resources(self, resource_data):
        resources = resource_data.get("Resources", {})
        how_to_resources = resources.get("How To", [])
        case_study_resources = resources.get("Case Study", [])

        for new_howto_data in how_to_resources:
            try:
                # Ensure mandatory fields are not None
                if any(key not in new_howto_data or new_howto_data[key] is None for key in
                       ["title", "summary", "link"]):
                    raise ValueError(f"Missing mandatory field for How To: {new_howto_data}")

                # Check if HowTo already exists
                try:
                    new_howto = HowTo.objects.get(title=new_howto_data["title"])
                except HowTo.DoesNotExist:
                    new_howto = HowTo(
                        title=new_howto_data["title"],
                        summary=new_howto_data["summary"],
                        link=new_howto_data["link"],
                        location_exact=new_howto_data.get("location_exact", True),
                    )

                # Handle location
                if location_data := new_howto_data.get('location'):  # Check if location key exists
                    lat = float(location_data["lat"])
                    lng = float(location_data["lng"])
                    new_howto.location = Point(lng, lat)

                new_howto.save()

                # Handle tags
                new_howto.tags.clear()  # Clear existing tags
                for tag_name in new_howto_data.get("tags", []):  # Ensure 'tags' is a list even if missing
                    tag = self.get_or_create_custom_tag(tag_name)
                    new_howto.tags.add(tag)

                new_howto.save()

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error loading How To '{new_howto_data.get('title', 'Unknown')}': {e}")
                )

        for new_casestudy_data in case_study_resources:
            try:
                # Ensure mandatory fields are not None
                if any(key not in new_casestudy_data or new_casestudy_data[key] is None for key in
                       ["title", "summary", "link", "body"]):
                    raise ValueError(f"Missing mandatory field for case study: {new_casestudy_data}")

                # Check if case study already exists
                try:
                    new_casestudy = CaseStudy.objects.get(title=new_casestudy_data["title"])
                except CaseStudy.DoesNotExist:
                    new_casestudy = CaseStudy(
                        title=new_casestudy_data["title"],
                        summary=new_casestudy_data["summary"],
                        link=new_casestudy_data["link"],
                        location_exact=new_casestudy_data.get("location_exact", True),
                    )

                # Handle image
                if (image_name := new_casestudy_data.get("image")):  # Check if image key exists
                    image_path = os.path.join(DATA_DIR, image_name)
                    if os.path.exists(image_path):  # Check if the image file exists
                        with open(image_path, "rb") as f:
                            img = Image.objects.get_or_create(
                                file=ImageFile(BytesIO(f.read()), name=image_name)
                            )[0]
                        new_casestudy.case_study_image = img
                    else:
                        new_casestudy.case_study_image = None

                if new_casestudy_data.get("body"):  # Check if body key exists
                    new_casestudy.body = [("body_text", {"content": RichText(new_casestudy_data["body"])})]

                new_casestudy.save()

                # Handle tags
                new_casestudy.tags.clear()  # Clear existing tags
                for tag_name in new_casestudy_data.get("tags", []):  # Ensure 'tags' is a list even if missing
                    tag = self.get_or_create_custom_tag(tag_name)
                    new_casestudy.tags.add(tag)

                new_casestudy.save()

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error loading case study '{new_casestudy_data.get('title', 'Unknown')}': {e}")
                )
