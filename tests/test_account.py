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
    # placeholder for when there's actually anything on the dashboard to check, feel free to comment out for now if it gets in the way
    #assert re.match(f'.*Welcome {test_user.display_name}', welcome, re.S)
    assert 'Your profile misses important data, please add them in' not in welcome
    test_user.year_of_birth = None
    test_user.post_code = None
    test_user.save()
    dash = client.get('/dashboard/')
    assert 'Messages' in str(dash.content)


def test_data_add(client, test_user):
    test_user.year_of_birth = None
    test_user.post_code = None
    test_user.save()
    client.force_login(test_user)
    print(test_user)
    print(client.post(reverse('account_add_data'), {'year_of_birth': 1997, 'post_code': 'AB12', 'organisation': 'None'}))
    print(test_user.year_of_birth)
    assert CustomUser.objects.get(id=test_user.id).year_of_birth == 1997
    assert CustomUser.objects.get(id=test_user.id).post_code.code == 'AB12 3CD'
    client.post(reverse('account_add_data'), {'year_of_birth': 2001, 'post_code': 'N4'})
    assert CustomUser.objects.get(id=test_user.id).year_of_birth == 1997
    assert CustomUser.objects.get(id=test_user.id).post_code.code == 'AB12 3CD'


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


'''
@pytest.mark.django_db
def test_update_flow(client, test_user):
    client.force_login(test_user)

    update_form = client.get(reverse('account_update'))
    #current_name = bs4.BeautifulSoup(update_form.content, features='html5lib').body.find("div").find('form', attrs={'hx-put': reverse('account_update')}).find("div").find("input", attrs={'name': 'display_name'})['value']
    current_name = bs4.BeautifulSoup(update_form.content, features='html5lib').body.find("div").find("form").find("div").find("input", attrs={'name': 'display_name'})['value']

    print(current_name == test_user.display_name)
    assert current_name == test_user.display_name
    print(client.put(reverse('account_update')))
    data = {'display_name': 'New Name', 'email': 'testemail@example.com'}
    client.put(reverse('account_update'), data)

    assert CustomUser.objects.get(id=test_user.id).display_name == 'New Name'
    # http://web.archive.org/web/20111224041840/http://www.techsupportteam.org/forum/digital-imaging-photography/1892-worlds-smallest-valid-jpeg.html
    # needs to be valid because avatar upload only accepts valid images in png, jpg or bmp
    #smallest_jpg = b"\xFF\xD8\xFF\xE0\x00\x10\x4A\x46\x49\x46\x00\x01\x01\x01\x00\x48\x00\x48\x00\x00\xFF\xDB\x00\x43\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xC2\x00\x0B\x08\x00\x01\x00\x01\x01\x01\x11\x00\xFF\xC4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xDA\x00\x08\x01\x01\x00\x01\x3F\x10"
    #avatar = SimpleUploadedFile("file.jpg", smallest_jpg, content_type="image/jpeg")
    #client.post(reverse('account_update'), {'avatar': avatar})
    #assert CustomUser.objects.get(id=test_user.id).avatar.read() == avatar.file.getvalue()
'''


@pytest.mark.django_db
def test_name_update_flow(client, test_user):
    client.force_login(test_user)

    update_form = client.get(reverse('account_update'))
    current_name = bs4.BeautifulSoup(update_form.content, features='html5lib').body.find("div").find("form").find("div").find("input", attrs={'name': 'display_name'})['value']
    assert current_name == test_user.display_name
    #data = {'display_name': 'New Name', 'email': 'testemail@example.com',}
    data = 'display_name=New Name&email=testemail%40example.com'
    client.put(reverse('account_update'), data)
    assert CustomUser.objects.get(id=test_user.id).display_name == 'New Name'



def test_delete_account(client, test_user):
    client.force_login(test_user)
    delete_page = client.get(reverse('account_delete'))
    assert 'Delete profile' in str(delete_page.content)
    client.post(reverse('account_delete'), {'confirm': 'confirm'})
    assert len(CustomUser.objects.filter(id=test_user.id)) == 0

