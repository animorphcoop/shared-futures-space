# tests for analytics

import pytest
from datetime import date

from django.urls import reverse
from allauth.account.admin import EmailAddress
from django.contrib.auth.hashers import make_password

from analytics.models import AnalyticsEvent, AnalyticsSession

@pytest.mark.django_db
def test_log_account_create(client):
    previous_events = AnalyticsEvent.objects.filter(type = AnalyticsEvent.EventType.SIGNUP)
    assert len(previous_events) == 0
    exclude_list = [evt.id for evt in previous_events] # force evaluation of the queryset
    client.post('/profile/signup/', {'email': 'testemail@example.com',
                                     'password1': 'test_password',
                                     'password2': 'test_password'})
    new_events = AnalyticsEvent.objects.filter(type = AnalyticsEvent.EventType.SIGNUP).exclude(id__in = exclude_list)
    assert len(new_events) == 1
    assert new_events[0].session.sessid_hash == '[no session]'

def test_log_login(client, test_user):
    previous_events = AnalyticsEvent.objects.filter(type = AnalyticsEvent.EventType.LOGIN)
    assert len(previous_events) == 0
    exclude_list = [evt.id for evt in previous_events] # force evaluation of the queryset
    client.post('/profile/login/', {'login': test_user.email,
                                    'password': 'test_password'}) # user passwords obviously not accessible as part of the object
    new_events = AnalyticsEvent.objects.filter(type = AnalyticsEvent.EventType.LOGIN).exclude(id__in = exclude_list)
    assert len(new_events) == 1
    assert new_events[0].session.sessid_hash == make_password(test_user.display_name, salt = str(date.today()))

def test_log_resource_access(client, test_user, other_test_user, test_how_to_resource):
    previous_events = AnalyticsEvent.objects.filter(type = AnalyticsEvent.EventType.RESOURCE)
    assert len(previous_events) == 0
    exclude_list = [evt.id for evt in previous_events] # force evaluation of the queryset
    client.get(reverse('resource_item', args=[test_how_to_resource.slug]))
    new_events = AnalyticsEvent.objects.filter(type = AnalyticsEvent.EventType.RESOURCE).exclude(id__in = exclude_list)
    assert len(new_events) == 0 # ignore non-users
    exclude_list += [evt.id for evt in new_events]
    client.force_login(test_user)
    client.get(reverse('resource_item', args=[test_how_to_resource.slug]))
    new_events = AnalyticsEvent.objects.filter(type = AnalyticsEvent.EventType.RESOURCE).exclude(id__in = exclude_list)
    assert len(new_events) == 1
    assert new_events[0].target_resource.title == test_how_to_resource.title
    assert new_events[0].session.sessid_hash == make_password(test_user.display_name, salt = str(date.today()))
    exclude_list += [evt.id for evt in new_events]
    client.get(reverse('resource_item', args=[test_how_to_resource.slug]))
    new_events = AnalyticsEvent.objects.filter(type = AnalyticsEvent.EventType.RESOURCE).exclude(id__in = exclude_list)
    assert len(new_events) == 0 # log only once per user per day
    exclude_list += [evt.id for evt in new_events]
    client.force_login(other_test_user)
    client.get(reverse('resource_item', args=[test_how_to_resource.slug]))
    new_events = AnalyticsEvent.objects.filter(type = AnalyticsEvent.EventType.RESOURCE).exclude(id__in = exclude_list)
    assert len(new_events) == 1 # but other users can still log their on accesses
    assert new_events[0].target_resource.title == test_how_to_resource.title
    assert new_events[0].session.sessid_hash == make_password(other_test_user.display_name, salt = str(date.today()))
