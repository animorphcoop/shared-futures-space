# tests for creating and working with an account

import re
import time

import bs4
import pytest
from action.models import Action
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from userauth.models import CustomUser
from userauth.util import get_system_user, slug_to_user, user_to_slug


@pytest.mark.django_db
@pytest.mark.usefixtures("celery_session_app")
@pytest.mark.usefixtures("celery_session_worker")
def test_create_account(client, mailoutbox):
    email_free = client.post(
        reverse("check_email"),
        {"email": "testemail@example.com"},
        HTTP_REFERER="/profile/signup/",
    )
    assert "" == email_free.content.decode("utf-8")
    response = client.post(
        "/profile/signup/",
        {
            "email": "testemail@example.com",
            "password1": "test_password",
            "password2": "test_password",
        },
    )
    time.sleep(6)  # ensure email has sent properly
    assert len(mailoutbox) == 1
    confirm_extraction = re.match(
        ".*(/profile/confirm-email/[_0-9a-zA-Z:-]+/).*", mailoutbox[0].body, re.S
    )
    assert type(confirm_extraction) == re.Match
    confirm_link = confirm_extraction.group(1)
    confirm_page = client.get(confirm_link).content
    post_link = (
        bs4.BeautifulSoup(confirm_page, "html5lib")
        .body.find("form", attrs={"method": "post"})
        .attrs["action"]
    )
    client.post(post_link)  # confirm email
    login_response = client.post(
        "/profile/login/",
        {"login": "testemail@example.com", "password": "test_password"},
    )
    assert login_response.status_code == 302
    assert login_response.url == "/dashboard/"
    email_free_now = client.post(
        reverse("check_email"),
        {"email": "testemail@example.com"},
        HTTP_REFERER="/profile/signup/",
    )
    assert (
        "This address is taken, please choose a different one."
        in email_free_now.content.decode("utf-8")
    )


def test_dashboard_info(client, test_user):
    client.force_login(test_user)
    dash = client.get("/dashboard/")
    assert dash.status_code == 200
    welcome = bs4.BeautifulSoup(dash.content, "html5lib").body.text
    assert "Your profile misses important data, please add them in" not in welcome
    test_user.year_of_birth = None
    test_user.post_code = None
    test_user.save()
    dash = client.get("/dashboard/")
    assert "View messages" in str(dash.content)


def test_data_add(client, test_user):
    test_user.year_of_birth = None
    test_user.post_code = None
    test_user.display_name = None
    test_user.organisation = None
    test_user.avatar = None
    test_user.added_data = False

    test_user.save()
    client.force_login(test_user)
    client.get(reverse("account_add_data"))  # just make sure getting that page is safe
    client.post(
        reverse("account_add_data"),
        {
            "display_name": "a test user",
            "year_of_birth": 1997,
            "post_code": "AB12",
            "avatar": "1",
            "organisation_name": "BIP",
            "organisation_url": "https://bip.org",
        },
    )
    assert CustomUser.objects.get(id=test_user.id).year_of_birth == 1997
    assert CustomUser.objects.get(id=test_user.id).post_code.code == "AB12"
    client.post(
        reverse("account_add_data"),
        {
            "display_name": "a test user",
            "year_of_birth": 1987,
            "post_code": "BT11b",
            "avatar": "3",
            "organisation_name": "CIR",
            "organisation_url": "https://cir.org",
        },
    )
    assert CustomUser.objects.get(id=test_user.id).year_of_birth == 1997
    assert CustomUser.objects.get(id=test_user.id).post_code.code == "AB12"


def test_account_info(client, test_user):
    info_page = client.get(
        reverse(
            "user_detail",
            args=[f'{test_user.display_name.replace(" ", "-")}-{test_user.pk}'],
        )
    )
    assert test_user.display_name in info_page.content.decode("utf-8")
    # assert str(test_user.year_of_birth) in info_page.content.decode('utf-8')
    # assert test_user.post_code.code in info_page.content.decode('utf-8')
    assert test_user.avatar.image_url in info_page.content.decode("utf-8")


# @pytest.mark.django_db
# def test_user_request_flow(client, test_user, admin_client):
#    client.force_login(test_user)
#    request_form = client.get(reverse('account_request'))
#    assert request_form.status_code == 200
#    make_request = client.post(reverse('account_request'),
#                               {'kind': 'make_editor',
#                                'reason': 'pls'})
#    assert make_request.status_code == 302
#    assert len(Action.objects.filter(kind='user_request_make_editor')) == 1
#
#    requests_page = admin_client.post(reverse('account_request_panel'), {'retrieve_messages': '', 'from': '0', 'interval': '10'})
#    requests_html = bs4.BeautifulSoup(requests_page.content, 'html5lib')
#    assert test_user.display_name + ' made a request: user_request_make_editor, because: pls' in requests_html.text
#    action_id = requests_html.find('input', {'type': 'hidden', 'name': 'action_id'})['value']
#    admin_client.post(reverse('do_action'), {'action_id': action_id, 'choice': 'invoke'})
#    #messages = client.post(reverse('user_chat', args=[user_to_slug(get_system_user())]), {'retrieve_messages': '', 'from': '0', 'interval': '10'})
#    messages = client.post(reverse('user_chat', args=[user_to_slug(test_user)]), {'retrieve_messages': '', 'from': '0', 'interval': '10'})
#    #assert 'your request to become an editor has been granted' in str(messages.content)


@pytest.mark.django_db
def test_name_update_flow(client, test_user):
    client.force_login(test_user)

    update_form = client.get(reverse("user_detail", args=[str(test_user.id)]))
    current_name = test_user.display_name
    assert current_name in update_form.content.decode("utf-8")
    data = "display_name=New Name&email=testemail%40example.com&avatar=" + str(
        test_user.avatar.id
    )
    client.put(reverse("account_update"), data)
    assert CustomUser.objects.get(id=test_user.id).display_name == "New Name"


def test_delete_account(client, test_user):
    client.force_login(test_user)
    delete_page = client.get(reverse("account_delete"))
    assert "Delete profile" in str(delete_page.content)

    client.post(reverse("account_delete"), {"confirm": "confirm"})
    assert len(CustomUser.objects.filter(id=test_user.id)) == 0
