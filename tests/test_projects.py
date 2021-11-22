# tests for the projects app workflows

import pytest
import bs4

from django.urls import reverse
from project.models import Project, ProjectOwnership

@pytest.mark.django_db
def test_project_create(client, test_user):
    initial_projects = [p for p in Project.objects.all()] # copying items to avoid later mutation
    client.force_login(test_user)
    created = client.post(reverse('new_project'), {'name': 'test project', 'description': 'this is a test'})
    assert created.status_code == 302
    assert created.url == reverse('all_projects')
    all_projects = Project.objects.all()
    added = [project for project in all_projects if project not in initial_projects]
    assert len(added) == 1
    assert added[0].name == 'test project'
    assert added[0].description == 'this is a test'
    ownerships = ProjectOwnership.objects.filter(project = added[0])
    assert len(ownerships) == 1
    assert ownerships[0].user == test_user

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
    ProjectOwnership.objects.create(user = test_user, project = test_project)
    attempt_logged_out = client.get(reverse('edit_project', args=[test_project.id]))
    assert attempt_logged_out.status_code == 302
    client.force_login(test_user)
    attempt_logged_in = client.get(reverse('edit_project', args=[test_project.id]))
    assert attempt_logged_in.status_code == 200
    client.post(reverse('edit_project', args=[test_project.id]), {'name': 'new edited name',
                                                                  'description': 'new edited description'})
    assert Project.objects.get(pk=test_project.id).name == 'new edited name'
