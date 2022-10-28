# tests for messaging system

import pytest
import bs4

from river.models import ProjectMembership
from userauth.util import slug_to_user, user_to_slug

from django.urls import reverse

import datetime
# !! river tests no longer applicable with no longer just the one chat per river, but needs to be replaced with something that checks all the stage chats

def test_project_chat_basics(client, test_user, test_river):
    test_river.start_envision()
    chat_url = reverse('river_chat', args=[test_river.slug, 'envision', 'general'])
    chat_page = client.get(chat_url)
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features='html5lib')
    assert '(you are not logged in)' in chat_page_html.text
    client.post(chat_url, {'message': 'test message'})
    chat_page = client.get(chat_url)
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features='html5lib')
    assert 'test message' not in chat_page_html.text # can't send message while not logged in
    client.force_login(test_user)
    client.post(chat_url, {'message': 'test message'})
    chat_page = client.get(chat_url)
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features='html5lib')
    assert 'test message' not in chat_page_html.text
    assert '(you are not a member of this chat)' in chat_page_html.text
    ProjectMembership.objects.create(river=test_river, user=test_user, starter=False)
    client.post(chat_url, {'message': 'test message'})
    chat_page = client.get(chat_url)
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features='html5lib')
    # name might not be displayed if it was you? Something to test differently (like in template checking who's issuing the request)
    #assert test_user.display_name in chat_page_html.text

    # can check date as the timestamp is used
    assert str(datetime.date.today().day) in  chat_page_html.text
    assert 'test message' in chat_page_html.text

def test_project_chat_interface(client, test_user, test_river):
    test_river.start_envision()
    test_river.start_plan()
    chat_url = reverse('river_chat', args=[test_river.slug, 'plan', 'funding'])
    ProjectMembership.objects.create(river=test_river, user=test_user, starter=False)
    client.force_login(test_user)
    for i in range(10):
        client.post(chat_url, {'message': 'test message ' + str(i)})
    chat_page = client.get(chat_url)
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features='html5lib')
    for i in range(10):
        assert 'test message ' + str(i) in chat_page_html.text
    chat_page = client.get(chat_url + '?interval=5')
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features='html5lib')
    for i in range(5):
        assert 'test message ' + str(i) not in chat_page_html.text
    for i in range(5,10):
        assert 'test message ' + str(i) in chat_page_html.text
    chat_page = client.get(chat_url + '?from=5')
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features='html5lib')
    for i in range(5):
        assert 'test message ' + str(i) in chat_page_html.text
    for i in range(5,10):
        assert 'test message ' + str(i) not in chat_page_html.text

def test_direct_chat_basics(client, test_user, other_test_user):
    from userauth.util import get_userpair # import here because importing from util is side-effecting on the db the first time it happens and pytest doesn't like that
    pair = get_userpair(other_test_user, test_user)
    chat_url = reverse('user_chat', args=[user_to_slug(other_test_user)])
    client.force_login(test_user)
    chat_page = client.get(chat_url)
    assert b'Private chat' in chat_page.content
    client.post(chat_url, {'message': 'test message'})
    client.force_login(other_test_user)
    chat_page = client.get(reverse('user_chat', args=[user_to_slug(test_user)]))
    assert b'Private chat' in chat_page.content
    assert b'test message' in chat_page.content

def test_direct_chat_interface(client, test_user, other_test_user):
    from userauth.util import get_userpair # import here because importing from util is side-effecting on the db the first time it happpens and pytest doesn't like that
    pair = get_userpair(test_user, other_test_user)
    chat_url = reverse('user_chat', args=[user_to_slug(other_test_user)])
    client.force_login(test_user)
    for i in range(10):
        client.post(chat_url, {'message': 'test message ' + str(i)})
    chat_page = client.get(chat_url)
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features='html5lib')
    for i in range(10):
        assert 'test message ' + str(i) in chat_page_html.text
    chat_page = client.get(chat_url + '?interval=5')
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features='html5lib')
    for i in range(5):
        assert 'test message ' + str(i) not in chat_page_html.text
    for i in range(5,10):
        assert 'test message ' + str(i) in chat_page_html.text
    chat_page = client.get(chat_url + '?from=5')
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features='html5lib')
    for i in range(5):
        assert 'test message ' + str(i) in chat_page_html.text
    for i in range(5,10):
        assert 'test message ' + str(i) not in chat_page_html.text

def test_direct_chat_listing(client, test_user, other_test_user):
    from userauth.util import get_userpair
    client.force_login(test_user)
    listing = client.get(reverse('account_all_chats'))
    assert 'Your Messages' in str(listing.content)
    assert other_test_user.display_name not in str(listing.content)
    get_userpair(test_user, other_test_user)
    listing = client.get(reverse('account_all_chats'))
    assert other_test_user.display_name in str(listing.content)





