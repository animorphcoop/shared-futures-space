import base64
from io import BytesIO

import pytest
from allauth.account.admin import EmailAddress
from area.models import PostCode
from django.core.files.images import ImageFile
from django.utils import timezone
from poll.models import MultipleChoicePoll, SingleChoicePoll
from resources.models import CaseStudy, HowTo
from river.models import River
from task.models import Task
from userauth.models import UserAvatar
from wagtail.images.models import Image

SMALLEST_JPG_BASE64 = b"/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAFA3PEY8MlBGQUZaVVBfeMiCeG5uePWvuZHI////////////////////////////////////////////////////wAALCAABAAEBAREA/8QAFAABAAAAAAAAAAAAAAAAAAAABP/EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAD8Aa//Z"


# a user account to use during testing
@pytest.fixture(scope="function")
def test_user(db, django_user_model):
    # http://web.archive.org/web/20111224041840/http://www.techsupportteam.org/forum/digital-imaging-photography/1892-worlds-smallest-valid-jpeg.html
    # needs to be valid because avatar upload only accepts valid images in png, jpg or bmp
    smallest_jpg = base64.b64decode(SMALLEST_JPG_BASE64)
    img_file = ImageFile(BytesIO(smallest_jpg), name="test image")
    avatar = UserAvatar.objects.create()
    avatar.avatar.save(name="test avatar", content=img_file)
    user = django_user_model.objects.create_user(
        username="test_user",
        email="test_user@email.com",
        avatar=avatar,
        password="test_password",
        display_name="Test User",
        year_of_birth=1999,
        post_code=PostCode.objects.create(code="AB12"),
        added_data=True,
    )
    user.save()
    EmailAddress.objects.create(
        email=user.email, verified=True, primary=True, user=user
    )  # make user verified

    return user


@pytest.fixture(scope="function")
def other_test_user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="other_test_user",
        email="other_test_user@email.com",
        password="other_test_password",
        display_name="Other Test User",
        year_of_birth=1998,
        post_code=PostCode.objects.create(code="PS7"),
        added_data=True,
    )


@pytest.fixture()
def admin_user(
    db: None,
    django_user_model,
    django_username_field: str,
):
    """This overrides the default pytest-django admin_user function [1] and
    enhances it with a field named "username", which in our case is required, in
    addition to our designated username field, which is "email".

    [1]: https://github.com/pytest-dev/pytest-django/blob/53373573f905ec5e0ec5786f49efdcdca5ae41fd/pytest_django/fixtures.py#L404-L432

    This function returns an existing user with username "admin", or creates a
    new one with password "password".
    """
    UserModel = django_user_model
    username_field = django_username_field
    username = "admin@example.com" if username_field == "email" else "admin"

    try:
        # The default behavior of `get_by_natural_key()` is to look up by `username_field`.
        # However the user model is free to override it with any sort of custom behavior.
        # The Django authentication backend already assumes the lookup is by username,
        # so we can assume so as well.
        user = UserModel._default_manager.get_by_natural_key(username)
    except UserModel.DoesNotExist:
        user_data = {}
        if "email" in UserModel.REQUIRED_FIELDS:
            user_data["email"] = "admin@example.com"
        user_data["password"] = "password"
        user_data[username_field] = username

        # in our case, username_field is "email"
        if username_field != "username":
            user_data["username"] = "admin"

        user = UserModel._default_manager.create_superuser(**user_data)
    return user


# items to use during testing
@pytest.fixture(scope="function")
def test_river(db):
    return River.objects.create(title="some river", description="river to do something")


@pytest.fixture(scope="function")
def create_test_task(db, test_user, test_river):
    def _create(
        river=test_river,
        responsible=test_user,
        stage_name="act",
        topic="general",
        name="Example Task",
        done=False,
        **kwargs,
    ):
        return Task.objects.create(
            river=river,
            responsible=responsible,
            stage_name=stage_name,
            topic=topic,
            name=name,
            done=done,
            **kwargs,
        )

    return _create


@pytest.fixture(scope="function")
def test_how_to_resource(db):
    how_to = HowTo.objects.create(
        title="howtitle",
        summary="not much to say, do it yourself",
        link="https://animorph.coop/",
    )
    how_to.tags.add("how to", "urban garden", "leisure")  # Use `add` method to assign tags
    return how_to


@pytest.fixture(scope="function")
def test_case_study_resource(db):
    return CaseStudy.objects.create(
        title="case study title",
        summary="not much to say, do it yourself",
        link="https://animorph.coop/",
    )


@pytest.fixture(scope="function")
def test_singlechoicepoll(db, test_river):
    return SingleChoicePoll.objects.create(
        question="is this a test question?",
        description="a test question",
        options=["option 1", "option 2"],
        expires=timezone.now() + timezone.timedelta(days=1),
        river=test_river,
    )


@pytest.fixture(scope="function")
def test_multiplechoicepoll(db, test_river):
    return MultipleChoicePoll.objects.create(
        question="which options?",
        description="a test questions",
        options=["option A", "option B"],
        expires=timezone.now() + timezone.timedelta(days=1),
        river=test_river,
    )


@pytest.fixture(scope="function")
def test_image(db):
    # http://web.archive.org/web/20111224041840/http://www.techsupportteam.org/forum/digital-imaging-photography/1892-worlds-smallest-valid-jpeg.html
    # needs to be valid because avatar upload only accepts valid images in png, jpg or bmp
    smallest_jpg = base64.b64decode(SMALLEST_JPG_BASE64)
    img_file = ImageFile(BytesIO(smallest_jpg), name="test image")
    return Image.objects.create(title="test image", file=img_file)


# make celery work
@pytest.fixture(scope="session")
def celery_config():
    return {
        "accept_content": ["pickle"],
        "task_serializer": "pickle",
        "result_serializer": "pickle",
    }
