# tests for using polls

import pytest
from django.urls import reverse
from poll.models import SingleChoicePoll, SingleVote, MultipleChoicePoll, MultipleVote
from river.models import ProjectMembership
from messaging.util import send_system_message

def test_create_poll(client, test_user, test_river):
    client.get(reverse('poll_create')) # make sure form doesn't crash while rendering
    client.force_login(test_user)
    # single choice
    new_poll = client.post(reverse('poll_create'), {'question': 'is this a test poll?', 'kind': 'SINGLE', 'options': '["answer 1","answer b","all of the above"]', 'expires': '01/02/2023 16:57', 'river': str(test_river.id)})
    assert new_poll.status_code == 302
    new_poll_redirect = client.get(new_poll.url)
    assert 'is this a test poll?' in new_poll_redirect.content.decode('utf-8')
    assert 'answer 1' in new_poll_redirect.content.decode('utf-8')
    assert 'poll is wrong' in new_poll_redirect.content.decode('utf-8')
    assert SingleChoicePoll.objects.filter(question = 'is this a test poll?').exists()
    # multiple choice
    new_poll = client.post(reverse('poll_create'), {'question': 'which of the following?', 'kind': 'MULTIPLE', 'options': '["answer 1","answer b","all of the above"]', 'expires': '01/02/2023 16:57', 'river': str(test_river.id)})
    assert new_poll.status_code == 302
    new_poll_redirect = client.get(new_poll.url)
    assert 'which of the following?' in new_poll_redirect.content.decode('utf-8')
    assert 'answer 1' in new_poll_redirect.content.decode('utf-8')
    assert 'poll is wrong' in new_poll_redirect.content.decode('utf-8')
    assert MultipleChoicePoll.objects.filter(question = 'which of the following?').exists()
    

def test_vote_poll_single(client, test_user, other_test_user, test_singlechoicepoll, test_river):
    test_river.start_envision()
    client.force_login(test_user)
    ProjectMembership.objects.create(river = test_river, user = test_user) # so we can see the chat with the poll in
    SingleVote.objects.create(poll = test_singlechoicepoll, user = test_user, choice = None)
    SingleVote.objects.create(poll = test_singlechoicepoll, user = other_test_user, choice = None)
    # can see the poll in chat
    send_system_message(test_river.envision_stage.chat, 'poll', context_poll = test_singlechoicepoll)
    chat_view = client.get(reverse('river_chat', args=[test_river.slug, 'envision', 'general']))
    assert 'is this a test question?' in chat_view.content.decode('utf-8')
    assert 'poll is wrong' in chat_view.content.decode('utf-8')
    # can vote on the poll, and it won't close
    client.post(reverse('poll_view', args=[test_singlechoicepoll.uuid]), {'choice': test_singlechoicepoll.options[0]})
    assert len(SingleVote.objects.filter(poll = test_singlechoicepoll, choice = 1)) == 1
    assert SingleChoicePoll.objects.get(id = test_singlechoicepoll.id).closed == False
    # can't vote if you don't have a vote entry established
    SingleVote.objects.get(poll = test_singlechoicepoll, user = test_user).delete()
    client.post(reverse('poll_view', args=[test_singlechoicepoll.uuid]), {'choice': test_singlechoicepoll.options[1]})
    assert len(SingleVote.objects.filter(poll = test_singlechoicepoll, user = test_user, choice = 2)) == 0
    assert SingleChoicePoll.objects.get(id = test_singlechoicepoll.id).closed == False
    # poll will close when it should
    client.force_login(other_test_user)
    client.post(reverse('poll_view', args=[test_singlechoicepoll.uuid]), {'choice': 'poll is wrong'})
    assert len(SingleVote.objects.filter(poll = test_singlechoicepoll, choice = 0)) == 1
    assert SingleChoicePoll.objects.get(id = test_singlechoicepoll.id).closed == True

def test_vote_poll_multiple(client, test_user, other_test_user, test_multiplechoicepoll, test_river):
    test_river.start_envision()
    client.force_login(test_user)
    ProjectMembership.objects.create(river = test_river, user = test_user) # so we can see the chat with the poll in
    ProjectMembership.objects.create(river = test_river, user = other_test_user)
    MultipleVote.objects.create(poll = test_multiplechoicepoll, user = test_user, choice = [])
    MultipleVote.objects.create(poll = test_multiplechoicepoll, user = other_test_user, choice = [])
    # can see the poll in chat
    send_system_message(test_river.envision_stage.chat, 'poll', context_poll = test_multiplechoicepoll)
    chat_view = client.get(reverse('river_chat', args=[test_river.slug, 'envision', 'general']))
    assert 'which options?' in chat_view.content.decode('utf-8')
    assert 'poll is wrong' in chat_view.content.decode('utf-8')
    # can vote on the poll, and it won't close
    client.post(reverse('poll_view', args=[test_multiplechoicepoll.uuid]), {'choice': test_multiplechoicepoll.options[0]})
    assert len(MultipleVote.objects.filter(poll = test_multiplechoicepoll, choice__contains = [1])) == 1
    assert len(MultipleVote.objects.filter(poll = test_multiplechoicepoll, choice__contains = [2])) == 0
    assert MultipleChoicePoll.objects.get(id = test_multiplechoicepoll.id).closed == False
    client.post(reverse('poll_view', args=[test_multiplechoicepoll.uuid]), {'choice': test_multiplechoicepoll.options[1]})
    assert len(MultipleVote.objects.filter(poll = test_multiplechoicepoll, choice__contains = [2])) == 1
    assert MultipleChoicePoll.objects.get(id = test_multiplechoicepoll.id).closed == False
    client.post(reverse('poll_view', args=[test_multiplechoicepoll.uuid]), {'choice': test_multiplechoicepoll.options[1]})
    assert len(MultipleVote.objects.filter(poll = test_multiplechoicepoll, choice__contains = [2])) == 0
    assert MultipleChoicePoll.objects.get(id = test_multiplechoicepoll.id).closed == False
    # can't vote if you don't have a vote entry established
    MultipleVote.objects.get(poll = test_multiplechoicepoll, user = test_user).delete()
    client.post(reverse('poll_view', args=[test_multiplechoicepoll.uuid]), {'choice': test_multiplechoicepoll.options[1]})
    assert len(MultipleVote.objects.filter(poll = test_multiplechoicepoll, user = test_user, choice__contains = [2])) == 0
    assert MultipleChoicePoll.objects.get(id = test_multiplechoicepoll.id).closed == False
    # poll will close when it should
    client.force_login(other_test_user)
    client.post(reverse('poll_view', args=[test_multiplechoicepoll.uuid]), {'choice': 'poll is wrong'})
    assert len(MultipleVote.objects.filter(poll = test_multiplechoicepoll, choice__contains = [0])) == 1
    assert MultipleChoicePoll.objects.get(id = test_multiplechoicepoll.id).closed == True
