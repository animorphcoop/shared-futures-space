# pyre-strict

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from uuid import uuid4

from messaging.models import Chat  # pyre-ignore[21]
from area.models import PostCode

from typing import List, Optional, Any, Dict


class CustomUser(AbstractUser):
    uuid: models.UUIDField = models.UUIDField(default=uuid4, editable=False)
    first_name: None = None
    last_name: None = None
    display_name: models.CharField = models.CharField(verbose_name=_("Display name"),
                                                      max_length=30, help_text=_("Will be shown alongside entries"),
                                                      null=True)
    year_of_birth: models.PositiveIntegerField = models.PositiveIntegerField(verbose_name=_("Year of birth"),
                                                                             validators=[MinValueValidator(1900)],
                                                                             null=True, blank=True)
    post_code: models.ForeignKey = models.ForeignKey(PostCode, on_delete = models.SET_NULL) #models.CharField = models.CharField(verbose_name=_("Post code"), max_length=8, null=True, blank=True)
    avatar: models.FileField = models.FileField(upload_to='accounts/avatars/', max_length=100, null=True, blank=True)

    editor: models.BooleanField = models.BooleanField(default=False)  # is this user an editor
    organisation: models.BooleanField = models.BooleanField(default=False)  # is this an organisation's account

    class Meta:
        ordering: List[str] = ['display_name']

    # to redirect to account profile page
    def get_absolute_url(self) -> str:
        return reverse('profile_view')

    def __str__(self) -> str:
        return f"{self.email}"


def new_chat() -> int:  # required because a plain Chat.objects.create or a lambda can't be serialised for migrations :(
    c = Chat()
    c.save()
    return c.id


class UserPair(models.Model):
    user1: models.ForeignKey = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='first_user')
    user2: models.ForeignKey = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='second_user')
    chat: models.ForeignKey = models.ForeignKey('messaging.Chat', null=True, on_delete=models.SET_NULL,
                                                default=new_chat)  # I'm guessing that if for some reason a chat is deleted, that means we want to purge it and replace it with a new one

    def save(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        # ensure that there won't be two UserPairs created for one pair of users
        if self.user1.uuid > self.user2.uuid:
            swp = self.user1.uuid
            self.user1.uuid = self.user2.uuid
            self.user2.uuid = swp
        return super().save(*args, **kwargs)  # pyre-ignore[6] destructuring arguments
