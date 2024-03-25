# tests for messaging system

import datetime

import bs4
from django.urls import reverse
from river.models import RiverMembership
from userauth.util import get_system_user, user_to_slug


def test_river_chat_basics(client, test_user, test_river):
    test_river.start_envision()
    chat_url = reverse("river_chat", args=[test_river.slug, "envision", "general"])
    chat_page = client.get(chat_url)
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features="html5lib")
    # assert 'Please log in to participate' in chat_page_html.text
    chat_page = client.post(chat_url, {"text": "test message", "retrieve_messages": ""})
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features="html5lib")
    assert (
        "test message" not in chat_page_html.text
    )  # can't send message while not logged in
    client.force_login(test_user)
    chat_page = client.post(chat_url, {"text": "test message", "retrieve_messages": ""})
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features="html5lib")
    assert "test message" not in chat_page_html.text
    RiverMembership.objects.create(river=test_river, user=test_user, starter=False)
    chat_page = client.post(chat_url, {"text": "test message", "retrieve_messages": ""})
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features="html5lib")
    # name might not be displayed if it was you? Something to test differently (like in template checking who's issuing the request)
    # assert test_user.display_name in chat_page_html.text

    # can check date as the timestamp is used
    assert str(datetime.date.today().day) in chat_page_html.text
    assert "test message" in chat_page_html.text


def test_river_chat_interface(client, test_user, test_river):
    get_system_user()  # needed to make sure it exists before we try to start_plan, since new polls reference it but can't create it if it doesn't exist for priority reasons
    test_river.start_envision()
    test_river.start_plan()
    chat_url = reverse("river_chat", args=[test_river.slug, "plan", "money"])
    RiverMembership.objects.create(river=test_river, user=test_user, starter=False)
    client.force_login(test_user)
    for i in range(21):
        client.post(chat_url, {"text": "test message " + str(i) + "."})
    chat_page = client.get(chat_url)
    for i in range(9):
        assert "test message " + str(i) + "." not in chat_page.content.decode("utf-8")
    for i in range(9, 21):
        assert "test message " + str(i) + "." in chat_page.content.decode("utf-8")
    chat_page = client.get(chat_url + "?page=1")
    for i in range(9):
        assert "test message " + str(i) + "." in chat_page.content.decode("utf-8")
    for i in range(9, 21):
        assert "test message " + str(i) + "." not in chat_page.content.decode("utf-8")


def test_direct_chat_basics(client, test_user, other_test_user):
    from userauth.util import (  # import here because importing from util is side-effecting on the db the first time it happens and pytest doesn't like that
        get_userpair,
    )

    get_userpair(other_test_user, test_user)
    client.force_login(test_user)
    client.post(
        reverse("user_chat", args=[user_to_slug(other_test_user)]),
        {"text": "test message"},
    )
    client.force_login(other_test_user)
    chat_page = client.get(reverse("user_chat", args=[user_to_slug(test_user)]))
    assert b"test message" in chat_page.content


def test_direct_chat_interface(client, test_user, other_test_user):
    from userauth.util import (  # import here because importing from util is side-effecting on the db the first time it happpens and pytest doesn't like that
        get_userpair,
    )

    get_userpair(test_user, other_test_user)
    chat_url = reverse("user_chat", args=[user_to_slug(other_test_user)])
    client.force_login(test_user)
    for i in range(20):
        client.post(chat_url, {"text": "test message " + str(i) + "."})
    chat_page = client.get(chat_url)
    for i in range(10):
        assert "test message " + str(i) + "." not in chat_page.content.decode("utf-8")
    for i in range(10, 20):
        assert "test message " + str(i) + "." in chat_page.content.decode("utf-8")
    chat_page = client.get(chat_url + "?page=1")
    for i in range(10):
        assert "test message " + str(i) + "." in chat_page.content.decode("utf-8")
    for i in range(10, 20):
        assert "test message " + str(i) + "." not in chat_page.content.decode("utf-8")


def test_direct_chat_listing(client, test_user, other_test_user):
    from userauth.util import get_userpair, user_to_slug

    client.force_login(test_user)
    listing = client.get(reverse("account_all_chats"))
    assert "Your Messages" in str(listing.content)
    assert other_test_user.display_name not in str(listing.content)
    get_userpair(test_user, other_test_user)
    client.post(
        reverse("user_chat", args=[user_to_slug(other_test_user)]),
        {"text": "test message"},
    )
    listing = client.get(reverse("account_all_chats"))
    assert other_test_user.display_name in str(listing.content)
