
# tests for pages being accessible or not depending on login

import pytest

@pytest.mark.django_db
@pytest.mark.parametrize('url,is_accessible', [('/',True),
                                               ('/account/login/',True),
                                               ('/dashboard/',False),
                                               ('/doesnotexist/',False)])
def test_access_public(url, is_accessible, client):
    if is_accessible:
        assert client.get(url).status_code == 200
    else:
        assert client.get(url).status_code != 200

@pytest.mark.django_db
@pytest.mark.parametrize('url,is_accessible', [('/',True),
                                               ('/dashboard/',True),
                                               ('/doesnotexist/',False)])
def test_access_logged_in(url, is_accessible, test_user, client):
    client.force_login(test_user)
    if is_accessible:
        assert client.get(url).status_code == 200
    else:
        assert client.get(url).status_code != 200
