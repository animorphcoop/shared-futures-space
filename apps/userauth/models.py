# pyre-strict

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from uuid import uuid4

from messaging.models import Chat # pyre-ignore[21]

from typing import List, Optional, Any, Dict


class CustomUser(AbstractUser):
    uuid = models.UUIDField(default = uuid4, editable = False)
    first_name: None = None  # pyre-ignore[15] remove these from the form, we use a single display_name instead
    last_name: None = None  # pyre-ignore[15] (pyre thinks this field can't be None in the parent class)
    display_name: models.CharField = models.CharField(verbose_name=_("Display name"),
                                                      max_length=30, help_text=_("Will be shown alongside entries"),
                                                      null=True)
    year_of_birth: models.PositiveIntegerField = models.PositiveIntegerField(verbose_name=_("Year of birth"),
                                                                             validators=[MinValueValidator(1900)],
                                                                             null=True, blank=True)
    post_code: models.CharField = models.CharField(verbose_name=_("Post code"), max_length=8, null=True, blank=True)
    avatar:  models.FileField = models.FileField(upload_to='accounts/avatars/', max_length=100, null=True, blank=True)

    editor: models.BooleanField = models.BooleanField(default=False) # is this user an editor

    class Meta:
        ordering: List[str] = ['display_name']

    # to redirect to account profile page
    def get_absolute_url(self) -> str:
        return reverse('profile_view')

    def __str__(self) -> str:
        return f"{self.display_name}"

# a request sent by a user to the admins for a change to their account
class UserRequest(models.Model):
    class Kind(models.TextChoices):
        OTHER = 'other', 'other'
        MAKE_EDITOR = 'make_editor', 'make_editor'
        CHANGE_POSTCODE = 'change_postcode', 'change_postcode'
        CHANGE_DOB = 'change_dob', 'change_dob'
    kind: models.CharField = models.CharField(max_length=15, choices = Kind.choices)
    reason: models.CharField = models.CharField(max_length=1000)
    date: models.DateTimeField = models.DateTimeField('date/time request made')
    user: models.ForeignKey = models.ForeignKey(CustomUser, on_delete = models.CASCADE)

def new_chat() -> int: # required because a plain Chat.objects.create or a lambda can't be serialised for migrations :(
    c = Chat()
    c.save()
    return c.id

class UserPair(models.Model):
    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name = 'first_user')
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name = 'second_user')
    chat = models.ForeignKey('messaging.Chat', null = True, on_delete = models.SET_NULL, default=new_chat) # I'm guessing that if for some reason a chat is deleted, that means we want to purge it and replace it with a new one
    def save(self, *args: List[Any], **kwargs: Dict[str,Any]) -> None:
        # ensure that there won't be two UserPairs created for one pair of users
        if self.user1.uuid > self.user2.uuid: # pyre-ignore[16]
            swp = self.user1.uuid
            self.user1.uuid = self.user2.uuid
            self.user2.uuid = swp
        return super().save(*args, **kwargs)

