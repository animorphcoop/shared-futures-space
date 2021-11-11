# tests for creating and working with an account

import pytest
import time
import bs4
import re

from django.urls import reverse
from userauth.models import UserRequest

@pytest.mark.django_db
@pytest.mark.usefixtures('celery_session_app')
@pytest.mark.usefixtures('celery_session_worker')
def test_create_account(client, mailoutbox):
    response = client.post('/account/signup/', {'email': 'testemail@example.com',
                                               'display_name': 'testuser',
                                               'password1': 'test_password',
                                               'password2': 'test_password'})
    time.sleep(6) # ensure email has sent properly
    assert len(mailoutbox) == 1
    confirm_extraction = re.match('.*(/account/confirm-email/[_0-9a-zA-Z:-]+/).*', mailoutbox[0].body, re.S)
    assert type(confirm_extraction) == re.Match
    confirm_link = confirm_extraction.group(1)
    confirm_page = client.get(confirm_link).content
    post_link = bs4.BeautifulSoup(confirm_page,'html5lib').body.find('form', attrs={'method':'post'}).attrs['action']
    client.post(post_link) # confirm email
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
    assert re.match(f'.*Welcome {test_user.display_name} born in {test_user.year_of_birth}.*', welcome, re.S)

@pytest.mark.django_db
def test_user_request_flow(client, test_user):
    client.force_login(test_user)
    request_form = client.get(reverse('account_request'))
    assert request_form.status_code == 200
    make_request = client.post(reverse('account_request'),
                               {'kind': 'make_moderator',
                                'reason': 'pls'})
    assert make_request.status_code == 302
    assert make_request.url == f'/account/{test_user.id}/update/'
    assert len(UserRequest.objects.all()) == 1
