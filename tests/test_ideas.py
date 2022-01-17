# tests for the projects app workflows

import pytest
import bs4

from django.urls import reverse
from django.conf import settings
from project.models import Idea, IdeaSupport, Project

@pytest.mark.django_db
def test_idea_create(client, test_user):
    initial_ideas = [i for i in Idea.objects.all()] # copying items to avoid later mutation
    client.force_login(test_user)
    created = client.post(reverse('new_idea'), {'name': 'test idea', 'description': 'this is a test'})
    assert created.status_code == 302
    assert created.url == reverse('all_ideas')
    all_ideas = Idea.objects.all()
    added = [idea for idea in all_ideas if idea not in initial_ideas]
    assert len(added) == 1
    assert added[0].name == 'test idea'
    assert added[0].description == 'this is a test'
    supporters = IdeaSupport.objects.filter(idea = added[0])
    assert len(supporters) == 1
    assert supporters[0].user == test_user

def test_idea_view(client, test_idea):
    ideas_page = client.get(reverse('all_ideas'))
    ideas_page_html = bs4.BeautifulSoup(ideas_page.content, features='html5lib')
    ideas = ideas_page_html.find('table', attrs={'id':'ideas'}).tbody.find_all('tr')[1:] # drop the headings row
    test_idea_row = [i for i in ideas if i.find('td').text == test_idea.name]
    assert len(test_idea_row) == 1
    single_idea_view = client.get(test_idea_row[0].find('a')['href'])
    single_idea_html = bs4.BeautifulSoup(single_idea_view.content, features='html5lib')
    assert single_idea_html.find('h3').text == f"Idea: {test_idea.name}"

def test_idea_edit(client, test_user, test_idea):
    test_idea.proposed_by = test_user
    attempt_logged_out = client.get(reverse('edit_idea', args=[test_idea.slug]))
    assert attempt_logged_out.status_code == 302
    client.force_login(test_user)
    attempt_logged_in = client.get(reverse('edit_idea', args=[test_idea.slug]))
    assert attempt_logged_in.status_code == 200
    client.post(reverse('edit_idea', args=[test_idea.slug]), {'action': 'update',
                                                            'name': 'new edited name',
                                                            'description': 'new edited description'})
    assert Idea.objects.get(pk=test_idea.id).name == 'new edited name'

def test_idea_support(client, test_user, other_test_user, test_idea):
    client.force_login(test_user)
    client.post(reverse('view_idea', args=[test_idea.slug]), {'action': 'give_support'})
    assert len(IdeaSupport.objects.filter(idea = test_idea)) == 1
    client.post(reverse('view_idea', args=[test_idea.slug]), {'action': 'give_support'})
    assert len(IdeaSupport.objects.filter(idea = test_idea)) == 1 # doesn't add more than one support from one person
    client.post(reverse('view_idea', args=[test_idea.slug]), {'action': 'remove_support'})
    assert len(IdeaSupport.objects.filter(idea = test_idea)) == 0 # successfully removes support
    for i in range(1, settings.PROJECT_REQUIRED_SUPPORTERS):
        s = IdeaSupport(user = other_test_user, idea = test_idea) # force create extra dummy supports all from one user
        s.save()
    client.post(reverse('view_idea', args=[test_idea.slug]), {'action': 'give_support'})
    assert len(IdeaSupport.objects.filter(idea=test_idea.id)) == 0
    assert len(Idea.objects.filter(id=test_idea.id)) == 0
    assert len(Project.objects.filter(slug=test_idea.slug)) == 1


    
    
