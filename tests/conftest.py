import pytest
from django.conf import settings

from django.core.files.images import ImageFile
from wagtail.images.models import Image
from django.utils import timezone
from io import BytesIO

from river.models import River
from area.models import PostCode, Area
from resources.models import HowTo, CaseStudy
from poll.models import SingleChoicePoll, MultipleChoicePoll
from userauth.models import UserAvatar
from allauth.account.admin import EmailAddress



# a user account to use during testing
@pytest.fixture(scope='function')
def test_user(db, django_user_model):
    # http://web.archive.org/web/20111224041840/http://www.techsupportteam.org/forum/digital-imaging-photography/1892-worlds-smallest-valid-jpeg.html
    # needs to be valid because avatar upload only accepts valid images in png, jpg or bmp
    smallest_jpg = b"\xFF\xD8\xFF\xE0\x00\x10\x4A\x46\x49\x46\x00\x01\x01\x01\x00\x48\x00\x48\x00\x00\xFF\xDB\x00\x43\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xC2\x00\x0B\x08\x00\x01\x00\x01\x01\x01\x11\x00\xFF\xC4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xDA\x00\x08\x01\x01\x00\x01\x3F\x10"
    img_file = ImageFile(BytesIO(smallest_jpg), name='test image')
    avatar = UserAvatar.objects.create()
    avatar.avatar.save(name = 'test avatar', content = img_file)
    user = django_user_model.objects.create_user(username='test_user', email='test_user@email.com', avatar = avatar,
                                                 password='test_password', display_name='Test User', year_of_birth=1999,
                                                 post_code=PostCode.objects.create(code="AB12"), added_data = True)
    user.save()
    EmailAddress.objects.create(email = user.email, verified = True, primary = True, user = user) # make user verified

    return user


@pytest.fixture(scope='function')
def other_test_user(db, django_user_model):
    return django_user_model.objects.create_user(username='other_test_user', email='other_test_user@email.com',
                                                 password='other_test_password', display_name='Other Test User',
                                                 year_of_birth=1998, post_code=PostCode.objects.create(code="PS7"),
                                                 added_data = True)


# items to use during testing
@pytest.fixture(scope='function')
def test_river(db):
    return River.objects.create(title='some river', description='river to do something')


@pytest.fixture(scope='function')
def test_how_to_resource(db):
    return HowTo.objects.create(title='howtitle', summary='not much to say, do it yourself',
                                link='https://animorph.coop/', tags=['how to', 'urban garden', 'leisure'])


@pytest.fixture(scope='function')
def test_case_study_resource(db):
    return CaseStudy.objects.create(title='case study title', summary='not much to say, do it yourself',
                                    link='https://animorph.coop/')

@pytest.fixture(scope='function')
def test_singlechoicepoll(db, test_river):
    return SingleChoicePoll.objects.create(question='is this a test question?', options = ['option 1', 'option 2'], expires = timezone.now() + timezone.timedelta(days=1), river=test_river)

@pytest.fixture(scope='function')
def test_multiplechoicepoll(db, test_river):
    return MultipleChoicePoll.objects.create(question='which options?', options = ['option A', 'option B'], expires = timezone.now() + timezone.timedelta(days=1), river=test_river)

@pytest.fixture(scope='function')
def test_image(db):
    # http://web.archive.org/web/20111224041840/http://www.techsupportteam.org/forum/digital-imaging-photography/1892-worlds-smallest-valid-jpeg.html
    # needs to be valid because avatar upload only accepts valid images in png, jpg or bmp
    smallest_jpg = b"\xFF\xD8\xFF\xE0\x00\x10\x4A\x46\x49\x46\x00\x01\x01\x01\x00\x48\x00\x48\x00\x00\xFF\xDB\x00\x43\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xC2\x00\x0B\x08\x00\x01\x00\x01\x01\x01\x11\x00\xFF\xC4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xDA\x00\x08\x01\x01\x00\x01\x3F\x10"
    img_file = ImageFile(BytesIO(smallest_jpg), name='test image')
    return Image.objects.create(title='test image', file=img_file)


# make celery work
@pytest.fixture(scope='session')
def celery_config():
    return {'accept_content': ['pickle'],
            'task_serializer': 'pickle',
            'result_serializer': 'pickle'}
