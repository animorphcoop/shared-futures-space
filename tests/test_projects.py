# tests for the projects app workflows

import pytest
import bs4

from django.urls import reverse
from project.models import Project, ProjectMembership
from userauth.util import user_to_slug

def test_project_view(client, test_project):
    projects_page = client.get(reverse('spring', args=[test_project.area.name]))
    assert test_project.name in projects_page.content.decode('utf-8')
    single_project_view = client.get(reverse('view_project', args=[test_project.slug]))
    assert test_project.description in single_project_view.content.decode('utf-8')

def test_project_edit(client, test_user, test_project):
    ProjectMembership.objects.create(user = test_user, project = test_project, owner = True)
    attempt_logged_out = client.get(reverse('edit_project', args=[test_project.slug]))
    assert attempt_logged_out.status_code == 302
    client.force_login(test_user)
    attempt_logged_in = client.get(reverse('edit_project', args=[test_project.slug]))
    assert attempt_logged_in.status_code == 200
    client.post(reverse('edit_project', args=[test_project.slug]), {'name': 'new edited name',
                                                                  'description': 'new edited description'})
    assert Project.objects.get(pk=test_project.id).name == 'new edited name'

def test_project_membership(client, test_user, other_test_user, test_project):
    # non-owner members
    client.force_login(test_user)
    project_page = client.get(reverse('view_project', args=[test_project.slug]))
    project_page_html = bs4.BeautifulSoup(project_page.content, features='html5lib')
    join_button = project_page_html.find('button')
    assert join_button.text == 'join project'
    client.post(reverse('view_project', args=[test_project.slug]), {'action': 'join'})
    assert len(ProjectMembership.objects.filter(user=test_user, project=test_project)) == 1
    project_page_member = client.get(reverse('view_project', args=[test_project.slug]))
    project_page_member_html = bs4.BeautifulSoup(project_page_member.content, features='html5lib')
    leave_button = project_page_member_html.find('button')
    assert leave_button.text == 'leave project'
    client.post(reverse('view_project', args=[test_project.slug]), {'action': 'leave'})
    assert len(ProjectMembership.objects.filter(user=test_user, project=test_project)) == 0
    # chat part no longer applicable now project chats are more complex, needs to be replaced once the new chat system is in place
    #chat_page = client.get(reverse('project_chat', args=[test_project.slug]))
    #assert test_user.display_name + ' left this project' in str(chat_page.content)
    # owners
    ownership = ProjectMembership(user=test_user, project=test_project, owner=True)
    other_ownership = ProjectMembership(user=other_test_user, project=test_project, owner=True)
    ownership.save()
    other_ownership.save()
    project_page_owner = client.get(reverse('view_project', args=[test_project.slug]))
    project_page_owner_html = bs4.BeautifulSoup(project_page_owner.content, features='html5lib')
    edit_link = project_page_owner_html.find_all('a')[0]
    assert edit_link.text == 'Edit Project'
    edit_page = client.get(reverse('edit_project', args=[test_project.slug]))
    edit_page_html = bs4.BeautifulSoup(edit_page.content, features='html5lib')
    abdicate_button = edit_page_html.find('button', attrs={'name': 'abdicate'})
    assert abdicate_button.text == 'Rescind Ownership'
    client.post(reverse('edit_project', args=[test_project.slug]), {'name': test_project.name,
                                                                    'description': test_project.description,
                                                                    'abdicate': 'abdicate'})
    assert ProjectMembership.objects.get(user=test_user, project=test_project).owner == False
    # chat part no longer applicable now project chats are more complex, needs to be replaced once the new chat system is in place
    #chat_page = client.get(reverse('project_chat', args=[test_project.slug]))
    #assert test_user.display_name + ' is no longer an owner of this project' in str(chat_page.content)
    client.force_login(other_test_user)
    edit_page_last_owner = client.get(reverse('edit_project', args=[test_project.slug]))
    edit_page_last_owner_html = bs4.BeautifulSoup(edit_page_last_owner.content, features='html5lib')
    assert 1 == len([p for p in edit_page_last_owner_html.find_all('p') if p.text == 'As you are the only owner of this project, you cannot rescind ownership'])
    client.post(reverse('edit_project', args=[test_project.slug]), {'name': test_project.name,
                                                                  'description': test_project.description,
                                                                  'abdicate': 'abdicate'}) # should be rejected
    assert ProjectMembership.objects.get(user=other_test_user, project=test_project).owner == True

def test_project_management(client, test_user, other_test_user, test_project):
    membership = ProjectMembership(user=test_user, project=test_project, owner=True, champion=False)
    other_membership = ProjectMembership(user=other_test_user, project=test_project, owner=False, champion=False)
    membership.save()
    other_membership.save()
    client.force_login(test_user)
    management_page = client.get(reverse('manage_project', args=[test_project.slug]))
    management_page_html = bs4.BeautifulSoup(management_page.content, features='html5lib')
    members = management_page_html.find('table', attrs={'id':'members'}).tbody.find_all('tr')[1:] # drop the headings row
    assert len(members) == 2
    client.post(reverse('manage_project', args=[test_project.slug]), {'membership': other_membership.id,
                                                                      'action': 'offer_championship'})
    client.force_login(other_test_user)
    user_chat = client.get(reverse('user_chat', args=[user_to_slug(test_user)]))
    user_chat_html = bs4.BeautifulSoup(user_chat.content, features='html5lib')
    action_id = user_chat_html.find('input', attrs={'type':'hidden', 'name':'action_id'})['value']
    client.post(reverse('do_action'), {'action_id': action_id, 'choice': 'invoke'})
    assert ProjectMembership.objects.get(user=other_test_user, project=test_project).champion

    client.post(reverse('manage_project', args=[test_project.slug]), {'membership': other_membership.id,
                                                                      'action': 'remove_championship'}) # should be rejected
    assert ProjectMembership.objects.get(user=other_test_user, project=test_project).champion
    client.force_login(test_user)
    client.post(reverse('manage_project', args=[test_project.slug]), {'membership': other_membership.id,
                                                                      'action': 'remove_championship'}) # should be accepted
    assert not ProjectMembership.objects.get(user=other_test_user, project=test_project).champion


def test_project_stages(test_project):
    test_project.start_envision()
    assert Project.objects.get(id = test_project.id).envision_stage is not None
    test_project.start_plan()
    assert Project.objects.get(id = test_project.id).plan_stage is not None
    test_project.start_act()
    assert Project.objects.get(id = test_project.id).act_stage is not None
    test_project.start_reflect()
    assert Project.objects.get(id = test_project.id).reflect_stage is not None
    








