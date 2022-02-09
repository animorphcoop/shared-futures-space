# tests for creating and working with an account

import pytest
import time
import bs4
import re

from django.urls import reverse
from userauth.models import CustomUser
from action.models import Action
from userauth.util import get_system_user
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
@pytest.mark.usefixtures('celery_session_app')
@pytest.mark.usefixtures('celery_session_worker')
def test_create_account(client, mailoutbox):
    response = client.post('/account/signup/', {'email': 'testemail@example.com',
                                                'email2': 'testemail@example.com',
                                                'display_name': 'testuser',
                                                'password1': 'test_password',
                                                'password2': 'test_password'})
    time.sleep(6)  # ensure email has sent properly
    assert len(mailoutbox) == 1
    confirm_extraction = re.match('.*(/account/confirm-email/[_0-9a-zA-Z:-]+/).*', mailoutbox[0].body, re.S)
    assert type(confirm_extraction) == re.Match
    confirm_link = confirm_extraction.group(1)
    confirm_page = client.get(confirm_link).content
    post_link = bs4.BeautifulSoup(confirm_page, 'html5lib').body.find('form', attrs={'method': 'post'}).attrs['action']
    client.post(post_link)  # confirm email
    login_response = client.post('/account/login/', {'login': 'testemail@example.com',
                                                     'password': 'test_password'})
    assert login_response.status_code == 302
    assert login_response.url == '/dashboard/'


def test_dashboard_info(client, test_user):
    client.force_login(test_user)
    dash = client.get('/dashboard/')
    assert dash.status_code == 200
    welcome = bs4.BeautifulSoup(dash.content, 'html5lib').body.text
    # janky as fuck placeholder for when there's actually anything on the dashboard to check, feel free to comment out for now if it gets in the way
    assert re.match(f'.*Welcome {test_user.display_name}', welcome, re.S)
    assert 'Your profile misses important data, please add them in' not in welcome
    test_user.year_of_birth = None
    test_user.post_code = None
    test_user.save()
    dash = client.get('/dashboard/')
    assert 'Your profile misses important data, please add them in' in str(dash.content)


def test_data_add(client, test_user):
    test_user.year_of_birth = None
    test_user.post_code = None
    test_user.save()
    client.force_login(test_user)
    client.post(reverse('account_data'), {'year_of_birth': 1997, 'post_code': 'ABC123'})
    assert CustomUser.objects.get(id=test_user.id).year_of_birth == 1997
    assert CustomUser.objects.get(id=test_user.id).post_code == 'ABC123'
    client.post(reverse('account_data'), {'year_of_birth': 2001, 'post_code': 'XYZ999'})
    assert CustomUser.objects.get(id=test_user.id).year_of_birth == 1997
    assert CustomUser.objects.get(id=test_user.id).post_code == 'ABC123'


@pytest.mark.django_db
def test_user_request_flow(client, test_user, admin_client):
    client.force_login(test_user)
    request_form = client.get(reverse('account_request'))
    assert request_form.status_code == 200
    make_request = client.post(reverse('account_request'),
                               {'kind': 'make_editor',
                                'reason': 'pls'})
    assert make_request.status_code == 302
    assert make_request.url == f'/account/update/'
    assert len(Action.objects.filter(kind='user_request_make_editor')) == 1

    requests_page = admin_client.get('/account/managerequests/')
    requests_html = bs4.BeautifulSoup(requests_page.content, 'html5lib')
    assert test_user.display_name + ' made a request: user_request_make_editor, because: pls' in requests_html.text
    action_id = requests_html.find('input', {'type': 'hidden', 'name': 'action_id'})['value']
    admin_client.post(reverse('do_action'), {'action_id': action_id, 'choice': 'invoke'})
    messages = client.get(reverse('user_chat', args=[get_system_user().uuid]))
    assert 'your request to become an editor has been granted' in str(messages.content)


@pytest.mark.django_db
def test_update_flow(client, test_user):
    client.force_login(test_user)
    update_form = client.get(reverse('account_update'))
    current_name = bs4.BeautifulSoup(update_form.content, features='html5lib').body.find('form', attrs={
        'action': reverse('account_update')}).find('input', attrs={'name': 'display_name'})['value']
    assert current_name == test_user.display_name
    client.post(reverse('account_update'), {'display_name': 'New Name'})
    assert CustomUser.objects.get(id=test_user.id).display_name == 'New Name'
    avatar = SimpleUploadedFile("file.mp4", b"file_content", content_type="video/mp4")
    client.post(reverse('account_update'), {'avatar': avatar})
    assert CustomUser.objects.get(id=test_user.id).avatar.read() == avatar.file.getvalue()

def test_delete_account(client, test_user):
    client.force_login(test_user)
    delete_page = client.get(reverse('account_delete'))
    assert 'Want to delete your account' in str(delete_page.content)
    client.post(reverse('account_delete'), {'confirm': 'confirm'})
    assert len(CustomUser.objects.filter(id=test_user.id)) == 0

