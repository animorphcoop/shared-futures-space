# pyre-strict

from django.db import models
from uuid import uuid4

from datetime import date, time
from django.http import HttpRequest
from typing import Type

from area.models import Area # pyre-ignore[21]
from userauth.models import CustomUser # pyre-ignore[21]


# we take request as an argument so that we can log the session if that turns out later to be necessary
def log_signup(new_user: CustomUser, request: HttpRequest) -> None: # pyre-ignore[11]
    AnalyticsEvent.objects.create(area = new_user.post_code.area if new_user.post_code else None, type = AnalyticsEvent.EventType.SIGNUP)

def log_login(request: HttpRequest) -> None:
    user = request.user
    AnalyticsEvent.objects.create(area = user.post_code.area if user.post_code else None, type = AnalyticsEvent.EventType.LOGIN) # pyre-ignore[16]

class AnalyticsEvent(models.Model):
    class EventType(models.TextChoices):
        SIGNUP = 'SIGNUP', 'signup'
        LOGIN = 'LOGIN', 'login'
    area: models.ForeignKey = models.ForeignKey(Area, on_delete = models.CASCADE, null = True)
    date: models.DateField = models.DateField(default = date.today)
    #hour: models.IntegerField = models.IntegerField(validators=[min_value(0), max_value(23)])
    type: models.CharField = models.CharField(max_length = 6, choices = EventType.choices)
