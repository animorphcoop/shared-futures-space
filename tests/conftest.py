import pytest
from django.conf import settings

from project.models import Project, Idea

# a user account to use during testing
@pytest.fixture(scope='function')
def test_user(db, django_user_model):
    return django_user_model.objects.create_user(username='test_user', email='test_user@email.com', password='test_password', display_name = 'Test User', year_of_birth = 1999, post_code = "AB123CD")
@pytest.fixture(scope='function')
def other_test_user(db, django_user_model):
    return django_user_model.objects.create_user(username='other_test_user', email='other_test_user@email.com', password='other_test_password', display_name = 'Other Test User', year_of_birth = 1998, post_code = "PSTCDE")

# items to use during testing
@pytest.fixture(scope='function')
def test_idea(db):
    return Idea.objects.create(name = 'some idea', description = 'idea to do something')
@pytest.fixture(scope='function')
def test_project(db):
    return Project.objects.create(name = 'some project', description = 'project to do something')

# make celery work
@pytest.fixture(scope='session')
def celery_config():
  return {'accept_content' : ['pickle'],
          'task_serializer' : 'pickle',
          'result_serializer' : 'pickle'}
