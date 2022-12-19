
# tests for pages being accessible or not depending on login

import pytest

#TODO: Landing now contains reverse url to springs which need to be added to db first via script

@pytest.mark.django_db
@pytest.mark.parametrize('url,is_accessible', [('/', True),
                                               ('/profile/login/', True),
                                               ('/dashboard/', False),
                                               ('/doesnotexist/', False),
                                               ('/search/?query=test', True),
                                               ('/profile/request/', False),
                                               ('/profile/managerequests/', False)])
def test_access_public(url, is_accessible, client):
    page = client.get(url)
    if is_accessible:
        assert page.status_code == 200 and 'Page not found' not in page.content.decode('utf-8')
    else:
        assert page.status_code != 200 or 'Page not found' in client.get(url).content.decode('utf-8')

@pytest.mark.django_db
@pytest.mark.parametrize('url,is_accessible', [('/', True),
                                               ('/doesnotexist/', False)])
def test_access_logged_in(url, is_accessible, test_user, client):
    page = client.get(url)
    print(page)
    print(page.content)
    if is_accessible:
        assert page.status_code == 200 and 'Page not found' not in page.content.decode('utf-8')
    else:
        assert page.status_code != 200 or 'Page not found' in client.get(url).content.decode('utf-8')

def test_access_admin_stuff(client, admin_client, test_user):
    client.force_login(test_user)
    assert 'You are not an admin' in str(client.get('/profile/managerequests/').content)
    assert 'You are not an admin' not in str(admin_client.get('/profile/managerequests/').content)
