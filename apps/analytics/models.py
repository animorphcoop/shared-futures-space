# pyre-strict

from django.db import models
from uuid import uuid4

from datetime import date, time

from area.models import Area


# we take request as an argument so that we can log the session if that turns out later to be necessary
def log_signup(request):
    new_user = request.user
    AnalyticsEvent.objects.create(area = new_user.post_code.area, type = AnalyticsEvent.EventType.SIGNUP)

def log_login(request):
    user = request.user
    AnalyticsEvent.objects.create(area = user.post_code.area, type = AnalyticsEvent.EventType.LOGIN)

class AnalyticsEvent(models.Model):
    class EventType(models.TextChoices):
        SIGNUP = 'SIGNUP', 'signup'
        LOGIN = 'LOGIN', 'login'
    area: models.ForeignKey = models.ForeignKey(Area, on_delete = models.CASCADE)
    date: models.DateField = models.DateField(default = date.today)
    #hour: models.IntegerField = models.IntegerField(validators=[min_value(0), max_value(23)])
    type: models.CharField = models.CharField(max_length = 6, choices = EventType.choices)
