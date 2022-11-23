from django.core.management.base import BaseCommand, CommandError
from wagtail.core.rich_text import RichText
from django.core.files.images import ImageFile
from wagtail.images.models import Image
from allauth.account.admin import EmailAddress
from django.utils import timezone
from io import BytesIO
from PIL import Image as PillowImage
import requests
import time
import json

from resources.models import HowTo, CaseStudy  # pyre-ignore[21]
from userauth.models import CustomUser, UserPair, Organisation, UserAvatar  # pyre-ignore[21]
from userauth.util import get_userpair # pyre-ignore[21]
from river.models import River, RiverMembership  # pyre-ignore[21]
from river.views import CreateEnvisionPollView # pyre-ignore[21]
from poll.models import SingleVote,SingleChoicePoll # pyre-ignore[21]
from messaging.models import Message  # pyre-ignore[21]
from area.models import PostCode, Area  # pyre-ignore[21]

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
                    new_casestudy.body.append(('body_text', {'content': RichText(new_casestudy_data['body'])}))

                    for tag in new_casestudy_data['tags']:
                        new_casestudy.tags.add(tag)
                    new_casestudy.save()

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


def add_rivers(rivers_data):
    for river_data in rivers_data:
        try:

            new_river = \
                River.objects.get_or_create(title=river_data['name'], description=river_data['description'],
                                            area=Area.objects.get_or_create(name=river_data['area'])[0])[0]

            for tag in river_data['tags']:
                new_river.tags.add(tag)

            if river_data['image'] != "":
                with open(image_dir + river_data['image'], 'rb') as f:
                    new_river.image = ImageFile(f)
                    new_river.save()
            else:
                new_river.save()

            for member in river_data['swimmers']:
                RiverMembership.objects.get_or_create(river=new_river,
                                                      user=CustomUser.objects.get(display_name=member))[0]
            for member in river_data['starters']:
                m = RiverMembership.objects.get_or_create(river=new_river,
                                                          user=CustomUser.objects.get(display_name=member))[0]
                m.starter = True
                m.save()
            if 'envision' in river_data:
                new_river.start_envision()
                for message in river_data['envision']['chat']:
                    Message.objects.get_or_create(sender=CustomUser.objects.get(display_name=message['from']),
                                                  text=message['content'], chat=new_river.envision_stage.chat)
                if 'poll' in river_data['envision']:
                    poll = SingleChoicePoll.objects.create(
                                question='is this an acceptable vision?',
                                description=river_data['envision']['poll']['description'],
                                options=['yes', 'no'],
                                invalid_option=False, expires=timezone.now() + timezone.timedelta(days=3),
                                river=new_river)
                    new_river.envision_stage.poll = poll
                    new_river.envision_stage.save()
                    for option in ['yes', 'no']:
                        for user in river_data['envision']['poll'][option]:
                            SingleVote.objects.filter(user = CustomUser.objects.get_or_create(display_name = user)[0],
                                                      poll = new_river.envision_stage.poll).update(choice = new_river.envision_stage.poll.options.index(option) + 1)

            if 'plan' in river_data:
                new_river.start_plan()
                for message in river_data['plan']['general']:
                    Message.objects.get_or_create(sender=CustomUser.objects.get(display_name=message['from']),
                                                  text=message['content'], chat=new_river.plan_stage.general_chat)
                for message in river_data['plan']['funding']:
                    Message.objects.get_or_create(sender=CustomUser.objects.get(display_name=message['from']),
                                                  text=message['content'], chat=new_river.plan_stage.funding_chat)
                for message in river_data['plan']['location']:
                    Message.objects.get_or_create(sender=CustomUser.objects.get(display_name=message['from']),
                                                  text=message['content'],
                                                  chat=new_river.plan_stage.location_chat)
                for message in river_data['plan']['dates']:
                    Message.objects.get_or_create(sender=CustomUser.objects.get(display_name=message['from']),
                                                  text=message['content'], chat=new_river.plan_stage.dates_chat)
            if 'act' in river_data:
                new_river.start_act()
                for message in river_data['act']['general']:
                    Message.objects.get_or_create(sender=CustomUser.objects.get(display_name=message['from']),
                                                  text=message['content'], chat=new_river.act_stage.general_chat)
                for message in river_data['act']['funding']:
                    Message.objects.get_or_create(sender=CustomUser.objects.get(display_name=message['from']),
                                                  text=message['content'], chat=new_river.act_stage.funding_chat)
                for message in river_data['act']['location']:
                    Message.objects.get_or_create(sender=CustomUser.objects.get(display_name=message['from']),
                                                  text=message['content'], chat=new_river.act_stage.location_chat)
                for message in river_data['act']['dates']:
                    Message.objects.get_or_create(sender=CustomUser.objects.get(display_name=message['from']),
                                                  text=message['content'], chat=new_river.act_stage.dates_chat)
            if 'reflect' in river_data:
                new_river.start_reflect()
                for message in river_data['reflect']['chat']:
                    Message.objects.get_or_create(sender=CustomUser.objects.get(display_name=message['from']),
                                                  text=message['content'], chat=new_river.reflect_stage.chat)

        except Exception as e:
            print('could not load river image: ' + str(river_data['name']) + '\nerror given: ' + repr(
                e))


def add_organisations(data):
    for org_data in data:
        try:
            Organisation.objects.get_or_create(name=org_data['name'], link=org_data['link'])
        except Exception as e:
            print('could not add organisation with definition: ' + str(org_data) + '\nerror given: ' + repr(e))


def add_avatars(avatars_data):
    for avatar_data in avatars_data:
        try:
            with open(image_dir + avatar_data['avatar'], 'rb') as f:
                new_avatar = UserAvatar.objects.create()
                new_avatar.avatar = ImageFile(f)
                new_avatar.save()
        except Exception as e:
            print('could not add avatar with definition: ' + str(avatar_data) + '\nerror given: ' + repr(e))


def add_users(users_data):
    for user_data in users_data:
        try:
            new_user = \
                CustomUser.objects.get_or_create(display_name=user_data['display name'], email=user_data['email'],
                                                 year_of_birth=user_data['year of birth'],
                                                 post_code=PostCode.objects.get_or_create(code=user_data['postcode'])[
                                                     0],
                                                 avatar=UserAvatar.objects.get_or_create(pk=user_data['avatar'])[0],
                                                 editor=user_data['editor'],
                                                 organisation=
                                                 Organisation.objects.get_or_create(name=user_data['organisation'])[
                                                     0] if 'organisation' in user_data else None,
                                                 added_data=True, username=user_data['display name'])[0]
            new_user.set_password(user_data['password'])
            new_user.save()
            eml = \
                EmailAddress.objects.get_or_create(email=user_data['email'], verified=True, primary=True,
                                                   user=new_user)[0]
            eml.save()
        except Exception as e:
            print('could not add user with definition: ' + str(user_data) + '\nerror given: ' + repr(e))


def add_areas(areas_data):
    for area_name in areas_data:
        try:
            this_area = Area.objects.get_or_create(name=area_name)[0]
            for postcode in areas_data[area_name]:
                PostCode.objects.get_or_create(code=postcode, area=this_area)
        except Exception as e:
            print('could not add area with definition: ' + str(areas_data[area_name]) + '\nerror given: ' + repr(e))


def add_relations(relations_data):
    for userchat_data in relations_data['User Chat']:
        try:
            pair = get_userpair(CustomUser.objects.get(display_name=userchat_data['user1']),
                                CustomUser.objects.get(display_name=userchat_data['user2']))
            for message in userchat_data['messages']:
                Message.objects.get_or_create(sender=CustomUser.objects.get(display_name=message['from']),
                                              text=message['content'], chat=pair.chat)
        except Exception as e:
            print('could not add userchat with definition: ' + str(userchat_data) + '\nerror given: ' + repr(e))


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
        add_organisations(data['Organisations'])
        add_avatars(data['User Avatars'])
        add_users(data['Users'])
        add_relations(data['Relations'])
        add_rivers(data['Rivers'])
