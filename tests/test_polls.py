# tests for using polls

import pytest
from django.urls import reverse
from poll.models import SingleChoicePoll, SingleVote, MultipleChoicePoll, MultipleVote
from project.models import ProjectMembership
from messaging.util import send_system_message

def test_create_poll(client, test_user, test_project):
    client.get(reverse('poll_create')) # make sure form doesn't crash while rendering
    client.force_login(test_user)
    # single choice
    new_poll = client.post(reverse('poll_create'), {'question': 'is this a test poll?', 'kind': 'SINGLE' 'options': '["answer 1","answer b","all of the above"]', 'expires': '01/02/2023 16:57', 'project': str(test_project.id)})
    assert new_poll.status_code == 302
    new_poll_redirect = client.get(new_poll.url)
    assert 'is this a test poll?' in new_poll_redirect.content.decode('utf-8')
    assert 'answer 1' in new_poll_redirect.content.decode('utf-8')
    assert 'poll is wrong' in new_poll_redirect.content.decode('utf-8')
    assert SingleChoicePoll.objects.filter(question = 'is this a test poll?').exists()
    # multiple choice
    new_poll = client.post(reverse('poll_create'), {'question': 'which of the following?', 'kind': 'MULTIPLE' 'options': '["answer 1","answer b","all of the above"]', 'expires': '01/02/2023 16:57', 'project': str(test_project.id)})
    assert new_poll.status_code == 302
    new_poll_redirect = client.get(new_poll.url)
    assert 'which of the following?' in new_poll_redirect.content.decode('utf-8')
    assert 'answer 1' in new_poll_redirect.content.decode('utf-8')
    assert 'poll is wrong' in new_poll_redirect.content.decode('utf-8')
    assert MultipleChoicePoll.objects.filter(question = 'which of the following?').exists()
    

def test_vote_poll_single(client, test_user, other_test_user, test_singlechoicepoll, test_project):
    test_project.start_envision()
    SingleVote.objects.create(poll = test_singlechoicepoll, user = test_user, choice = None)
    SingleVote.objects.create(poll = test_singlechoicepoll, user = other_test_user, choice = None)
    # can see the poll in chat
    send_system_message(test_project.envision_stage.chat, 'poll', context_poll = test_singlechoicepoll)
    chat_view = client.get(reverse('project_chat', args=[test_project.slug, 'envision', 'general']))
    assert 'is this a test question?' in chat_view.content.decode('utf-8')
    assert 'poll is wrong' in chat_view.content.decode('utf-8')
    # can vote on the poll, and it won't close
    client.force_login(test_user)
    client.post(reverse('poll_view', args=[test_singlechoicepoll.uuid]), {'choice': test_singlechoicepoll.options[0]})
    assert len(Vote.objects.filter(poll = test_singlechoicepoll, choice = 1)) == 1
    assert SingleChoicePoll.objects.get(id = test_singlechoicepoll.id).closed == False
    # can't vote if you don't have a vote entry established
    SingleVote.objects.get(poll = test_singlechoicepoll, user = test_user).delete()
    client.post(reverse('poll_view', args=[test_singlechoicepoll.uuid]), {'choice': test_singlechoicepoll.options[1]})
    assert len(Vote.objects.filter(poll = test_singlechoicepoll, user = test_user, choice = 2)) == 0
    assert SingleChoicePoll.objects.get(id = test_singlechoicepoll.id).closed == False
    # poll will close when it should
    client.force_login(other_test_user)
    client.post(reverse('poll_view', args=[test_singlechoicepoll.uuid]), {'choice': 'poll is wrong'})
    assert len(Vote.objects.filter(poll = test_singlechoicepoll, choice = 0)) == 1
    assert SingleChoicePoll.objects.get(id = test_singlechoicepoll.id).closed == True

def test_vote_poll_mutliple(client, test_user, other_test_user, test_multiplechoicepoll, test_project):
    test_project.start_envision()
    MultipleVote.objects.create(poll = test_multiplechoicepoll, user = test_user, choice = [])
    MultipleVote.objects.create(poll = test_multiplechoicepoll, user = other_test_user, choice = [])
    # can see the poll in chat
    send_system_message(test_project.envision_stage.chat, 'poll', context_poll = test_multiplechoicepoll)
    chat_view = client.get(reverse('project_chat', args=[test_project.slug, 'envision', 'general']))
    assert 'which options?' in chat_view.content.decode('utf-8')
    assert 'poll is wrong' in chat_view.content.decode('utf-8')
    # can vote on the poll, and it won't close
    client.force_login(test_user)
    client.post(reverse('poll_view', args=[test_multiplechoicepoll.uuid]), {'choice': test_singlechoicepoll.options[0]})
    assert len(Vote.objects.filter(poll = test_multiplechoicepoll, choice = 1)) == 1
    assert len(Vote.objects.filter(poll = test_multiplechoicepoll, choice = 2)) == 0
    assert MultipleChoicePoll.objects.get(id = test_multiplechoicepoll.id).closed == False
    client.post(reverse('poll_view', args=[test_multiplechoicepoll.uuid]), {'choice': test_singlechoicepoll.options[1]})
    assert len(Vote.objects.filter(poll = test_multiplechoicepoll, choice = 2)) == 1
    assert MultipleChoicePoll.objects.get(id = test_multiplechoicepoll.id).closed == False
    client.post(reverse('poll_view', args=[test_multiplechoicepoll.uuid]), {'choice': test_singlechoicepoll.options[1]})
    assert len(Vote.objects.filter(poll = test_multiplechoicepoll, choice = 2)) == 0
    assert MultipleChoicePoll.objects.get(id = test_multiplechoicepoll.id).closed == False
    # can't vote if you don't have a vote entry established
    MultipleVote.objects.get(poll = test_multiplechoicepoll, user = test_user).delete()
    client.post(reverse('poll_view', args=[test_multiplechoicepoll.uuid]), {'choice': test_singlechoicepoll.options[1]})
    assert len(Vote.objects.filter(poll = test_multiplechoicepoll, user = test_user, choice = 2)) == 0
    assert MultipleChoicePoll.objects.get(id = test_multiplechoicepoll.id).closed == False
    # poll will close when it should
    client.force_login(other_test_user)
    client.post(reverse('poll_view', args=[test_multiplechoicepoll.uuid]), {'choice': 'poll is wrong'})
    assert len(Vote.objects.filter(poll = test_multiplechoicepoll, choice = 0)) == 1
    assert MultipleChoicePoll.objects.get(id = test_multiplechoicepoll.id).closed == True
