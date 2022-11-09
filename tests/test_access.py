
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
    if is_accessible:
        assert client.get(url).status_code == 200
    else:
        assert client.get(url).status_code != 200

@pytest.mark.django_db
@pytest.mark.parametrize('url,is_accessible', [('/', False),
                                               ('/dashboard/', True),
                                               ('/doesnotexist/', False),
                                               ('/profile/request/', True)])
def test_access_logged_in(url, is_accessible, test_user, client):
    client.force_login(test_user)
    if is_accessible:
        assert client.get(url).status_code == 200
    else:
        assert client.get(url).status_code != 200

def test_access_admin_stuff(client, admin_client, test_user):
    client.force_login(test_user)
    assert 'You are not an admin' in str(client.get('/profile/managerequests/').content)
    assert 'You are not an admin' not in str(admin_client.get('/profile/managerequests/').content)
