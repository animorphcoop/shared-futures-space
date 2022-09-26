# pyre-strict

from django.contrib.auth.hashers import make_password
from django.contrib.auth import user_logged_in
from django.dispatch import receiver
from django.db import models
from uuid import uuid4

from datetime import date, time
from django.http import HttpRequest
from typing import Type, Dict, Any, Union

from area.models import Area # pyre-ignore[21]
from userauth.models import CustomUser # pyre-ignore[21]
from resources.models import Resource # pyre-ignore[21]



# we take request as an argument so that we can log the session if that turns out later to be necessary
# this is also why we can't hook a post_save signal for this, it doesn't have access to the request
def log_signup(new_user: CustomUser) -> None: # pyre-ignore[11]
    analyticsSession = AnalyticsSession.objects.get_or_create(sessid_hash = '[no session]', area = new_user.post_code.area if new_user.post_code else None)[0]
    AnalyticsEvent.objects.create(session = analyticsSession, type = AnalyticsEvent.EventType.SIGNUP)

# use a signal here because django provides stuff for logins so there's not really a good exposed place to put the call
@receiver(user_logged_in)
def log_login(sender: Type[CustomUser], request: HttpRequest, user: CustomUser, **kwargs: Dict[str,Any]) -> None:
    analyticsSession = AnalyticsSession.objects.get_or_create(sessid_hash = make_password(user.display_name, salt = str(date.today())), area = user.post_code.area if user.post_code else None)[0]
    AnalyticsEvent.objects.create(session = analyticsSession, type = AnalyticsEvent.EventType.LOGIN)

def log_resource_access(resource: Resource, user: CustomUser) -> None: # pyre-ignore[11]
    analyticsSession = AnalyticsSession.objects.get_or_create(sessid_hash = make_password(user.display_name, salt = str(date.today())), area = user.post_code.area if user.post_code else None)[0]
    if not AnalyticsEvent.objects.filter(session = analyticsSession, type = AnalyticsEvent.EventType.RESOURCE, target_resource = resource).exists():
        AnalyticsEvent.objects.create(session = analyticsSession, date = date.today(), type = AnalyticsEvent.EventType.RESOURCE, target_resource = resource)


class AnalyticsSession(models.Model):
    sessid_hash: models.CharField = models.CharField(max_length = 128) # hash of user.display_name salted with date.today(), so unique per user per day
    area: models.ForeignKey = models.ForeignKey(Area, on_delete = models.CASCADE, null = True)

class AnalyticsEvent(models.Model):
    class EventType(models.TextChoices):
        SIGNUP = 'SIGNUP', 'signup'
        LOGIN = 'LOGIN', 'login'
        RESOURCE = 'RESOURCE', 'resource'
    session: models.ForeignKey = models.ForeignKey(AnalyticsSession, on_delete = models.SET_NULL, null = True)
    date: models.DateField = models.DateField(default = date.today)
    type: models.CharField = models.CharField(max_length = 8, choices = EventType.choices)
    target_resource: models.ForeignKey = models.ForeignKey(Resource, on_delete = models.SET_NULL, null = True)
