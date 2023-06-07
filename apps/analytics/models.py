from datetime import date, time
from typing import Any, Dict, Type, Union
from uuid import uuid4

from area.models import Area
from django.contrib.auth import user_logged_in
from django.contrib.auth.hashers import make_password
from django.db import models
from django.dispatch import receiver
from django.http import HttpRequest
from resources.models import Resource
from userauth.models import CustomUser

####
## HOW THIS WORKS
#
# when an event that we want to record for analytic purposes occurs, a corresponding function in the LOGGING FUNCTIONS section should be invoked.
# this can happen either by catching a signal (as shown in the case of log_login) or simply by calling the function from whatever bit of code is
# responsible for making the event to be logged happen (as with eg. log_signup in the save function of CustomSignupForm in userauth/forms.py).
# these functions are responsible for recording the relevant information as an AnalyticsEvent, specifying who did what and when.
# the logging functions are very simple, but they are written here rather than in the places they get invoked from to ensure we know in a single place
# what events are logged and how.

####
## LOGGING FUNCTIONS
#


# we take request as an argument so that we can log the session if that turns out later to be necessary
# this is also why we can't hook a post_save signal for this, it doesn't have access to the request
def log_signup(new_user: CustomUser) -> None:
    analyticsSession = AnalyticsSession.objects.get_or_create(
        sessid_hash="[no session]",
        area=new_user.post_code.area if new_user.post_code else None,
    )[0]
    AnalyticsEvent.objects.create(
        session=analyticsSession, type=AnalyticsEvent.EventType.SIGNUP
    )


# use a signal here because django provides stuff for logins so there's not really a good exposed place to put the call
@receiver(user_logged_in)
def log_login(
    sender: Type[CustomUser],
    request: HttpRequest,
    user: CustomUser,
    **kwargs: Dict[str, Any]
) -> None:
    analyticsSession = AnalyticsSession.objects.get_or_create(
        sessid_hash=make_password(user.display_name, salt=str(date.today())),
        area=user.post_code.area if user.post_code else None,
    )[0]
    AnalyticsEvent.objects.create(
        session=analyticsSession, type=AnalyticsEvent.EventType.LOGIN
    )


def log_resource_access(resource: Resource, user: CustomUser) -> None:
    analyticsSession = AnalyticsSession.objects.get_or_create(
        sessid_hash=make_password(user.display_name, salt=str(date.today())),
        area=user.post_code.area if user.post_code else None,
    )[0]
    if not AnalyticsEvent.objects.filter(
        session=analyticsSession,
        type=AnalyticsEvent.EventType.RESOURCE,
        target_resource=resource,
    ).exists():
        AnalyticsEvent.objects.create(
            session=analyticsSession,
            date=date.today(),
            type=AnalyticsEvent.EventType.RESOURCE,
            target_resource=resource,
        )


def log_visit(user):
    analytics_session, _ = AnalyticsSession.objects.get_or_create(
        sessid_hash=make_password(user.display_name, salt=str(date.today())),
        area=user.post_code.area if user.post_code else None,
    )
    AnalyticsEvent.objects.get_or_create(
        session=analytics_session, type=AnalyticsEvent.EventType.VISIT
    )


def has_visited_today(user):
    analytics_session, _ = AnalyticsSession.objects.get_or_create(
        sessid_hash=make_password(user.display_name, salt=str(date.today())),
        area=user.post_code.area if user.post_code else None,
    )
    return AnalyticsEvent.objects.filter(
        session=analytics_session,
        type=AnalyticsEvent.EventType.VISIT,
    ).exists()


####
## MODELS
#


# an AnalyticsSession records a single user on a single day, without revealing which user but recording their broad location in case it's of interest. we don't
# connect the same user's activity between days, for privacy reasons
class AnalyticsSession(models.Model):
    sessid_hash: models.CharField = models.CharField(
        max_length=128
    )  # hash of user.display_name salted with date.today(), so unique per user per day
    area: models.ForeignKey = models.ForeignKey(
        Area, on_delete=models.CASCADE, null=True
    )


class AnalyticsEvent(models.Model):
    class EventType(models.TextChoices):
        SIGNUP = "SIGNUP", "signup"
        LOGIN = "LOGIN", "login"
        RESOURCE = "RESOURCE", "resource"
        VISIT = "VISIT", "visit"

    session: models.ForeignKey = models.ForeignKey(
        AnalyticsSession, on_delete=models.SET_NULL, null=True
    )
    date: models.DateField = models.DateField(default=date.today)
    type: models.CharField = models.CharField(max_length=8, choices=EventType.choices)
    target_resource: models.ForeignKey = models.ForeignKey(
        Resource, on_delete=models.SET_NULL, null=True
    )
