# tests for the projects app workflows

import pytest
import bs4

from django.urls import reverse
from project.models import Project, ProjectMembership

def test_project_view(client, test_project):
    projects_page = client.get(reverse('all_projects'))
    projects_page_html = bs4.BeautifulSoup(projects_page.content, features='html5lib')
    projects = projects_page_html.find('table', attrs={'id':'projects'}).tbody.find_all('tr')[1:] # drop the headings row
    test_project_row = [p for p in projects if p.find('td').text == test_project.name]
    assert len(test_project_row) == 1
    single_project_view = client.get(test_project_row[0].find('a')['href'])
    single_project_html = bs4.BeautifulSoup(single_project_view.content, features='html5lib')
    assert single_project_html.find('h3').text == f"Project: {test_project.name}"

def test_project_edit(client, test_user, test_project):
    ProjectMembership.objects.create(user = test_user, project = test_project, owner = True)
    attempt_logged_out = client.get(reverse('edit_project', args=[test_project.id]))
    assert attempt_logged_out.status_code == 302
    client.force_login(test_user)
    attempt_logged_in = client.get(reverse('edit_project', args=[test_project.id]))
    assert attempt_logged_in.status_code == 200
    client.post(reverse('edit_project', args=[test_project.id]), {'name': 'new edited name',
                                                                  'description': 'new edited description'})
    assert Project.objects.get(pk=test_project.id).name == 'new edited name'
