import pytest
from django.conf import settings

from project.models import Project, Idea
from area.models import PostCode, Area
from resources.models import HowTo, CaseStudy
from itertools import chain


# a user account to use during testing
@pytest.fixture(scope='function')
def test_user(db, django_user_model):
    return django_user_model.objects.create_user(username='test_user', email='test_user@email.com',
                                                 password='test_password', display_name='Test User', year_of_birth=1999,
                                                 post_code=PostCode.objects.create(code="AB123CD"))


@pytest.fixture(scope='function')
def other_test_user(db, django_user_model):
    return django_user_model.objects.create_user(username='other_test_user', email='other_test_user@email.com',
                                                 password='other_test_password', display_name='Other Test User',
                                                 year_of_birth=1998, post_code=PostCode.objects.create(code="PS7C0DE"))


# items to use during testing
@pytest.fixture(scope='function')
def test_idea(db):
    return Idea.objects.create(name='some idea', description='idea to do something')


@pytest.fixture(scope='function')
def test_project(db):
    return Project.objects.create(name='some project', description='project to do something')


'''

@pytest.fixture(scope='function')
def test_how_to_resource(db):
    return HowTo.objects.create(title='howtitle', summary='not much to say, do it yourself',
                                    link='https://animorph.coop/', tags=['how to', 'urban garden', 'leisure'])

@pytest.fixture(scope='function')
def test_case_study_resource(db):
    return CaseStudy.objects.create(title='case study title', summary='not much to say, do it yourself',
                                             link='https://animorph.coop/', tags=['case study', 'advice', 'enterprise'])

@pytest.fixture(scope='function')
def test_how_to_resources(db):
    how_tos = [HowTo.objects.create(title='howtitle', summary='not much to say, do it yourself',
                                    link='https://animorph.coop/', tags=['how to', 'urban garden', 'leisure']),
               HowTo.objects.create(title='howtitle2', summary='not much to say, do it yourself2',
                                    link='https://animorph.coop/', tags=['how to', 'community', 'organising'])
               ]
    return how_tos

@pytest.fixture(scope='function')
def test_case_study_resources(db):
    case_studies = [CaseStudy.objects.create(title='case study title', summary='not much to say, do it yourself',
                                             link='https://animorph.coop/', tags=['case study', 'advice', 'enterprise']),
                    CaseStudy.objects.create(title='case study title2', summary='not much to say, do it yourself2',
                                             link='https://animorph.coop/', tags=['case study', 'community', 'sustainability'])
                    ]
    return case_studies

@pytest.fixture(scope='function')
def test_resources():
    how_tos = test_how_to_resources()
    case_studies = test_case_study_resources()
    return list(chain(how_tos, case_studies))
'''


# make celery work
@pytest.fixture(scope='session')
def celery_config():
    return {'accept_content': ['pickle'],
            'task_serializer': 'pickle',
            'result_serializer': 'pickle'}
