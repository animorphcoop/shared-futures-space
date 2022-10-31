import pytest
from django.urls import reverse

from action.models import Action
from river.models import RiverMembership

def test_invoke_action(client, test_user, other_test_user, test_river):
    client.force_login(test_user)
    act = Action.objects.create(creator=other_test_user, receiver=test_user, kind='become_starter', param_river=test_river)
    RiverMembership.objects.create(user=test_user, river=test_river, starter=False)
    assert Action.objects.get(id=act.id).result == None
    client.post(reverse('do_action'), {'action_id': act.uuid, 'choice': 'invoke'})
    assert RiverMembership.objects.get(user=test_user, river=test_river).starter == True
    assert Action.objects.get(id=act.id).result == 'invoked'

def test_reject_action(client, test_user, other_test_user, test_river):
    client.force_login(test_user)
    act = Action.objects.create(creator=other_test_user, receiver=test_user, kind='become_starter', param_river=test_river)
    RiverMembership.objects.create(user=test_user, river=test_river, starter=False)
    assert Action.objects.get(id=act.id).result == None
    client.post(reverse('do_action'), {'action_id': act.uuid, 'choice': 'reject'})
    assert RiverMembership.objects.get(user=test_user, river=test_river).starter == False
    assert Action.objects.get(id=act.id).result == 'rejected'

def test_rescind_action(client, test_user, other_test_user, test_river):
    client.force_login(test_user)
    act = Action.objects.create(creator=test_user, receiver=other_test_user, kind='become_starter', param_river=test_river)
    RiverMembership.objects.create(user=test_user, river=test_river, starter=False)
    assert Action.objects.get(id=act.id).result == None
    client.post(reverse('do_action'), {'action_id': act.uuid, 'choice': 'retract'})
    assert RiverMembership.objects.get(user=test_user, river=test_river).starter == False
    assert Action.objects.get(id=act.id).result == 'rescinded'
    try:
        client.post(reverse('do_action'), {'action_id': act.uuid, 'choice': 'invoke'})
        assert False # previous line should throw
    except Exception as e:
        assert type(e) == Action.DoesNotExist
    assert RiverMembership.objects.get(user=test_user, river=test_river).starter == False
    assert Action.objects.get(id=act.id).result == 'rescinded'
