# pyre-strict

from django.contrib.auth import user_logged_in
from django.dispatch import receiver
from django.db import models
from uuid import uuid4

from datetime import date, time
from django.http import HttpRequest
from typing import Type, Dict, Any

from area.models import Area # pyre-ignore[21]
from userauth.models import CustomUser # pyre-ignore[21]
from resources.models import Resource # pyre-ignore[21]



# we take request as an argument so that we can log the session if that turns out later to be necessary
# this is also why we can't hook a post_save signal for this, it doesn't have access to the request
def log_signup(new_user: CustomUser, request: HttpRequest) -> None: # pyre-ignore[11]
    AnalyticsEvent.objects.create(area = new_user.post_code.area if new_user.post_code else None, type = AnalyticsEvent.EventType.SIGNUP)

# use a signal here because django provides stuff for logins so there's not really a good exposed place to put the call
@receiver(user_logged_in)
def log_login(sender: Type[CustomUser], request: HttpRequest, user: CustomUser, **kwargs: Dict[str,Any]) -> None:
    AnalyticsEvent.objects.create(area = user.post_code.area if user.post_code else None, type = AnalyticsEvent.EventType.LOGIN) # pyre-ignore[16]

class AnalyticsEvent(models.Model):
    class EventType(models.TextChoices):
        SIGNUP = 'SIGNUP', 'signup'
        LOGIN = 'LOGIN', 'login'
    area: models.ForeignKey = models.ForeignKey(Area, on_delete = models.CASCADE, null = True)
    date: models.DateField = models.DateField(default = date.today)
    #hour: models.IntegerField = models.IntegerField(validators=[min_value(0), max_value(23)])
    type: models.CharField = models.CharField(max_length = 6, choices = EventType.choices)
    target_resource: models.ForeignKey = models.ForeignKey(Resource, on_delete = models.SET_NULL, null = True)

class AnalyticsSession(models.Model):
    sessid_hash: models.CharField = models.CharField(max_length = 128) # from django.contrib.auth.hashers import make_password
    area: models.ForeignKey = models.ForeignKey(Area, on_delete = models.CASCADE, null = True)
