from django.core.management.base import BaseCommand, CommandError
from wagtail.core.rich_text import RichText
from django.core.files.images import ImageFile
from wagtail.images.models import Image
from allauth.account.admin import EmailAddress
from io import BytesIO
from PIL import Image as PillowImage
import requests
import json

from resources.models import HowTo, CaseStudy # pyre-ignore[21]
from userauth.models import CustomUser, UserPair # pyre-ignore[21]
from project.models import Project, ProjectMembership # pyre-ignore[21]
from messaging.models import Message # pyre-ignore[21]

#data = {'Resources':
#           {'How To': [{'title': 'test how to 1', 'summary': 'this resource helps you to do something', 'tags': ['resource', 'useful']},
#                      {'title': 'test how to 2', 'summary': 'this resource points you to an external project', 'tags': ['resource', 'organisation']}],
#            'Case Study': [{'title': 'test case study 1', 'summary': 'a case study of studying cases', 'image': 'ignore/example1.webp', 'body': 'body <b>texttt</b>', 'tags': ['case study', 'not useful']}]},
#        'Users': [{'display name': 'test_asa', 'email': 'fake@email.com', 'year of birth': 1999, 'postcode': 'BT17 OLE', 'editor': False, 'organisation': False, 'password': 'P@ssword!'},
#                  {'display name': 'some person', 'email': 'other@email.com', 'year of birth': 1987, 'postcode': 'BT17 OLF', 'editor': True, 'organisation': False, 'password': 'P@ssword!'}],
#        'Projects': [{'name': 'test project A', 'description': 'a project to do A', 'tags': ['project', 'A']},
#                     {'name': 'test project B', 'description': 'a project that will do B', 'tags': ['project', 'B']}],
#        'Relations':
#            {'Project Membership': [{'Project': 'test project A', 'User': 'test_asa', 'owner': False, 'champion': True}],
#             'User Chat' : [{'user1': 'test_asa', 'user2': 'some person'}]}}

def add_resources(resource_data):
    for new_howto_data in resource_data['How To']:
        new_howto = HowTo.objects.get_or_create(title = new_howto_data['title'], summary = new_howto_data['summary'])[0]
        for tag in new_howto_data['tags']:
            new_howto.tags.add(tag)
        new_howto.save()
    for new_casestudy_data in resource_data['Case Study']:
        with open(new_casestudy_data['image'], 'rb') as f:
            pimg = PillowImage.open(new_casestudy_data['image'])
            img = Image.objects.get_or_create(file = ImageFile(BytesIO(f.read()), name=new_casestudy_data['image']), width = pimg.width, height = pimg.height)[0]
        new_casestudy = CaseStudy.objects.get_or_create(title = new_casestudy_data['title'], summary = new_casestudy_data['summary'], case_study_image = img)[0]
        new_casestudy.body.append(('body_text', {'content':RichText(new_casestudy_data['body'])}))
        for tag in new_casestudy_data['tags']:
            new_casestudy.tags.add(tag)
        new_casestudy.save()

def add_projects(projects_data):
    for project_data in projects_data:
        new_project = Project.objects.get_or_create(name = project_data['name'], description = project_data['description'])[0]
        for tag in project_data['tags']:
            new_project.tags.add(tag)
        new_project.save()

def add_users(users_data):
    for user_data in users_data:
        new_user = CustomUser.objects.get_or_create(display_name = user_data['display name'], email = user_data['email'], year_of_birth = user_data['year of birth'],
                                                    post_code = user_data['postcode'], editor = user_data['editor'], organisation = user_data['organisation'],
                                                    username = user_data['display name'])[0]
        new_user.set_password(user_data['password'])
        new_user.save()
        eml = EmailAddress.objects.get_or_create(email = user_data['email'], verified = True, primary = True, user = new_user)[0]
        eml.save()

def add_relations(relations_data):
    for projectmembership_data in relations_data['Project Membership']:
        ProjectMembership.objects.get_or_create(project = Project.objects.get(name = projectmembership_data['Project']),
                                                user = CustomUser.objects.get(display_name = projectmembership_data['User']),
                                                owner = projectmembership_data['owner'], champion = projectmembership_data['champion'])[0]
        Message.objects.create(sender = CustomUser.objects.get(display_name = projectmembership_data['User']), text = 'hello! :)', chat = Project.objects.get(name = projectmembership_data['Project']).chat)
    for userchat_data in relations_data['User Chat']:
        pair = UserPair.objects.get_or_create(user1 = CustomUser.objects.get(display_name = userchat_data['user1']),
                                              user2 = CustomUser.objects.get(display_name = userchat_data['user2']))[0]
        Message.objects.create(sender = CustomUser.objects.get(display_name = userchat_data['user1']), text = 'hello! :)', chat = pair.chat)

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
            f.close()
        except:
            print('could not read from file: ' + options['datafile'])

        add_resources(data['Resources'])
        add_users(data['Users'])
        add_projects(data['Projects'])
        add_relations(data['Relations'])
