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

def test_project_membership(client, test_user, other_test_user, test_project):
    # non-owner members
    client.force_login(test_user)
    membership = ProjectMembership(user=test_user, project=test_project, owner=False)
    membership.save()
    project_page_member = client.get(reverse('view_project', args=[test_project.id]))
    project_page_member_html = bs4.BeautifulSoup(project_page_member.content, features='html5lib')
    leave_button = project_page_member_html.find('button')
    assert leave_button.text == 'leave project'
    client.post(reverse('view_project', args=[test_project.id]), {'action': 'leave'})
    assert len(ProjectMembership.objects.filter(user=test_user, project=test_project)) == 0
    # owners
    ownership = ProjectMembership(user=test_user, project=test_project, owner=True)
    other_ownership = ProjectMembership(user=other_test_user, project=test_project, owner=True)
    ownership.save()
    other_ownership.save()
    project_page_owner = client.get(reverse('view_project', args=[test_project.id]))
    project_page_owner_html = bs4.BeautifulSoup(project_page_owner.content, features='html5lib')
    edit_link = project_page_owner_html.find('a')
    assert edit_link.text == 'Edit Project'
    edit_page = client.get(reverse('edit_project', args=[test_project.id]))
    edit_page_html = bs4.BeautifulSoup(edit_page.content, features='html5lib')
    abdicate_button = edit_page_html.find('button', attrs={'name': 'abdicate'})
    assert abdicate_button.text == 'Rescind Ownership'
    client.post(reverse('edit_project', args=[test_project.id]), {'name': test_project.name,
                                                                  'description': test_project.description,
                                                                  'abdicate': 'abdicate'})
    assert ProjectMembership.objects.get(user=test_user, project=test_project).owner == False
    client.force_login(other_test_user)
    edit_page_last_owner = client.get(reverse('edit_project', args=[test_project.id]))
    edit_page_last_owner_html = bs4.BeautifulSoup(edit_page_last_owner.content, features='html5lib')
    assert 1 == len([p for p in edit_page_last_owner_html.find_all('p') if p.text == 'As you are the only owner of this project, you cannot rescind ownership'])
    client.post(reverse('edit_project', args=[test_project.id]), {'name': test_project.name,
                                                                  'description': test_project.description,
                                                                  'abdicate': 'abdicate'}) # should be rejected
    assert ProjectMembership.objects.get(user=other_test_user, project=test_project).owner == True

def test_project_management(client, test_user, other_test_user, test_project):
    membership = ProjectMembership(user=test_user, project=test_project, owner=True, champion=False)
    other_membership = ProjectMembership(user=other_test_user, project=test_project, owner=False, champion=True)
    membership.save()
    other_membership.save()
    client.force_login(test_user)
    management_page = client.get(reverse('manage_project', args=[test_project.id]))
    management_page_html = bs4.BeautifulSoup(management_page.content, features='html5lib')
    members = management_page_html.find('table', attrs={'id':'members'}).tbody.find_all('tr')[1:] # drop the headings row
    assert len(members) == 2
    client.force_login(other_test_user)
    client.post(reverse('manage_project', args=[test_project.id]), {'membership': other_membership.id,
                                                                    'action': 'remove_championship'}) # should be rejected
    assert ProjectMembership.objects.get(user=other_test_user, project=test_project).champion
    client.force_login(test_user)
    client.post(reverse('manage_project', args=[test_project.id]), {'membership': other_membership.id,
                                                                    'action': 'remove_championship'}) # should be accepted
    assert not ProjectMembership.objects.get(user=other_test_user, project=test_project).champion
    











    
