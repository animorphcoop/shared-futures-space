from django.core.management.base import BaseCommand, CommandError
from wagtail.core.rich_text import RichText
from django.core.files.images import ImageFile
from wagtail.images.models import Image
from allauth.account.admin import EmailAddress
from io import BytesIO
from PIL import Image as PillowImage
import requests
import json

from resources.models import HowTo, CaseStudy
from userauth.models import CustomUser, UserPair, Organisation, UserAvatar
from river.models import River, RiverMembership
from messaging.models import Message
from area.models import PostCode, Area

image_dir = 'autoupload/'


def add_resources(resource_data):
    for new_howto_data in resource_data['How To']:
        try:
            new_howto = HowTo.objects.get_or_create(title=new_howto_data['title'], summary=new_howto_data['summary'],
                                                    link=new_howto_data['link'])[0]
            for tag in new_howto_data['tags']:
                new_howto.tags.add(tag)
            new_howto.save()
        except Exception as e:
            print('could not add howto with definition: ' + str(new_howto_data) + '\nerror given: ' + repr(e))
    for new_casestudy_data in resource_data['Case Study']:
        if new_casestudy_data['image'] != "":
            try:
                with open(image_dir + new_casestudy_data['image'], 'rb') as f:
                    pimg = PillowImage.open(image_dir + new_casestudy_data['image'])
                    img = \
                        Image.objects.get_or_create(file=ImageFile(BytesIO(f.read()), name=new_casestudy_data['image']),
                                                    width=pimg.width, height=pimg.height)[0]
                    new_casestudy = \
                        CaseStudy.objects.get_or_create(title=new_casestudy_data['title'],
                                                        summary=new_casestudy_data['summary'],
                                                        case_study_image=img, link=new_casestudy_data['link'])[0]
            except Exception as e:
                print('could not load case study image: ' + str(new_casestudy_data['title']) + '\nerror given: ' + repr(
                    e))
        else:
            print(str(new_casestudy_data['title']) + " has no image")
            new_casestudy = \
                CaseStudy.objects.get_or_create(title=new_casestudy_data['title'],
                                                summary=new_casestudy_data['summary'], link=new_casestudy_data['link'])[
                    0]

        new_casestudy.body.append(('body_text', {'content': RichText(new_casestudy_data['body'])}))

        for tag in new_casestudy_data['tags']:
            new_casestudy.tags.add(tag)
        new_casestudy.save()

def add_avatars(avatars_data):
    for avatar_data in avatars_data:
        try:
            with open(image_dir + avatar_data['avatar'], 'rb') as f:
                new_avatar = UserAvatar.objects.create()
                new_avatar.avatar = ImageFile(f)
                new_avatar.save()
        except Exception as e:
            print('could not add avatar with definition: ' + str(avatar_data) + '\nerror given: ' + repr(e))

def add_areas(areas_data):
    for area_name in areas_data:
        try:
            this_area = Area.objects.get_or_create(name=area_name)[0]
            for postcode in areas_data[area_name]:
                PostCode.objects.get_or_create(code=postcode, area=this_area)
        except Exception as e:
            print('could not add area with definition: ' + str(areas_data[area_name]) + '\nerror given: ' + repr(e))



class Command(BaseCommand):
    help = 'import data'

    def add_arguments(self, parser):
        parser.add_argument('datafile', nargs='?', type=str, default='upload_conf.json')

    def handle(self, *args, **options):
        try:
            f = open(options['datafile'])
            try:
                data = json.load(f)
            except:
                print('could not parse valid json from ' + options['datafile'])
                exit()
            f.close()
        except:
            print('could not read from file: ' + options['datafile'])
            exit()

        add_areas(data['Areas'])
        add_resources(data['Resources'])
        add_avatars(data['User Avatars'])

