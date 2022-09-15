# tests for using polls

import pytest
from django.urls import reverse
from poll.models import Poll, Vote
from project.models import ProjectMembership

def test_create_poll(client, test_user, test_project):
    client.get(reverse('poll_create')) # make sure form doesn't crash while rendering
    client.force_login(test_user)
    new_poll = client.post(reverse('poll_create'), {'question': 'is this a test poll?', 'options': '["answer 1","answer b","all of the above"]', 'expires': '01/02/2023 16:57', 'project': str(test_project.id)})
    assert new_poll.status_code == 302
    new_poll_redirect = client.get(new_poll.url)
    assert 'is this a test poll?' in new_poll_redirect.content.decode('utf-8')
    assert 'answer 1' in new_poll_redirect.content.decode('utf-8')
    assert 'poll is wrong' in new_poll_redirect.content.decode('utf-8')
    assert Poll.objects.get(question = 'is this a test poll?').voter_num == len(ProjectMembership.objects.filter(project = test_project))
