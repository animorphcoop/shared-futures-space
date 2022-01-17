# tests for messaging system

import pytest
import bs4

from project.models import ProjectMembership

from django.urls import reverse

def test_project_chat_basics(client, test_user, test_project):
    chat_url = reverse('project_chat', args=[test_project.slug])
    chat_page = client.get(chat_url)
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features='html5lib')
    assert chat_page_html.find('h3').text == 'Project Chat: ' + test_project.name
    assert '(you must sign in to contribute)' in chat_page_html.text
    client.post(chat_url, {'message': 'test message'})
    chat_page = client.get(chat_url)
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features='html5lib')
    assert 'test message' not in chat_page_html.text # can't send message while not logged in
    client.force_login(test_user)
    client.post(chat_url, {'message': 'test message'})
    chat_page = client.get(chat_url)
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features='html5lib')
    assert 'test message' not in chat_page_html.text
    assert '(you must be a member of this project to contribute)' in chat_page_html.text
    ProjectMembership.objects.create(project=test_project, user=test_user, champion=False, owner=False)
    client.post(chat_url, {'message': 'test message'})
    chat_page = client.get(chat_url)
    chat_page_html = bs4.BeautifulSoup(chat_page.content, features='html5lib')
    assert test_user.display_name + ': test message' in chat_page_html.text
