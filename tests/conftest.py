import pytest
from django.conf import settings

@pytest.fixture(scope='function')
def test_user(db, django_user_model):
    return django_user_model.objects.create_user(username='test_user', email='test_user@email.com', password='test_password', display_name = 'Test User', year_of_birth = 1999, post_code = "AB123CD")

@pytest.fixture(scope='session')
def celery_config():
  return {'accept_content' : ['pickle'],
          'task_serializer' : 'pickle',
          'result_serializer' : 'pickle'}
