# tests for using polls

import pytest
from django.urls import reverse
from poll.models import Poll, Vote
from project.models import ProjectMembership
from messaging.util import send_system_message

def test_create_poll(client, test_user, test_project):
    client.get(reverse('poll_create')) # make sure form doesn't crash while rendering
    client.force_login(test_user)
    new_poll = client.post(reverse('poll_create'), {'question': 'is this a test poll?', 'options': '["answer 1","answer b","all of the above"]', 'expires': '01/02/2023 16:57', 'project': str(test_project.id)})
    assert new_poll.status_code == 302
    new_poll_redirect = client.get(new_poll.url)
    assert 'is this a test poll?' in new_poll_redirect.content.decode('utf-8')
    assert 'answer 1' in new_poll_redirect.content.decode('utf-8')
    assert 'poll is wrong' in new_poll_redirect.content.decode('utf-8')

def test_vote_poll(client, test_user, other_test_user, test_poll, test_project):
    test_project.start_envision()
    Vote.objects.create(poll = test_poll, user = test_user, choice = None)
    Vote.objects.create(poll = test_poll, user = other_test_user, choice = None)
    # can see the poll in chat
    send_system_message(test_project.envision_stage.chat, 'poll', context_poll = test_poll)
    chat_view = client.get(reverse('project_chat', args=[test_project.slug, 'envision', 'general']))
    assert 'is this a test question?' in chat_view.content.decode('utf-8')
    assert 'poll is wrong' in chat_view.content.decode('utf-8')
    # can vote on the poll, and it won't close
    client.force_login(test_user)
    client.post(reverse('poll_view', args=[test_poll.uuid]), {'choice': test_poll.options[0]})
    assert len(Vote.objects.filter(poll = test_poll, choice = 1)) == 1
    assert Poll.objects.get(id = test_poll.id).closed == False
    # can't vote if you don't have a vote entry established
    Vote.objects.get(poll = test_poll, user = test_user).delete()
    client.post(reverse('poll_view', args=[test_poll.uuid]), {'choice': test_poll.options[1]})
    assert len(Vote.objects.filter(poll = test_poll, user = test_user, choice = 2)) == 0
    assert Poll.objects.get(id = test_poll.id).closed == False
    # poll will close when it should
    client.force_login(other_test_user)
    client.post(reverse('poll_view', args=[test_poll.uuid]), {'choice': 'poll is wrong'})
    assert len(Vote.objects.filter(poll = test_poll, choice = 0)) == 1
    assert Poll.objects.get(id = test_poll.id).closed == True
