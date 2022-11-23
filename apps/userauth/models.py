# pyre-strict

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from uuid import uuid4

from messaging.models import Chat  # pyre-ignore[21]
from area.models import PostCode  # pyre-ignore[21]

from typing import List, Optional, Any, Dict, Optional


class Organisation(models.Model):
    uuid: models.UUIDField = models.UUIDField(default=uuid4)
    name: models.CharField = models.CharField(max_length=100)
    link: models.URLField = models.URLField()

    def __str__(self) -> str:
        return self.name


class UserAvatar(models.Model):
    avatar: models.ImageField = models.ImageField(upload_to='profile/avatars/', max_length=100, null=True, blank=True)

    @property
    def image_url(self) -> Optional[str]:
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url


class CustomUser(AbstractUser):
    uuid: models.UUIDField = models.UUIDField(default=uuid4, editable=False)
    first_name: None = None
    last_name: None = None
    signup_date: models.DateTimeField = models.DateTimeField(
        auto_now_add=True
    )
    added_data: models.BooleanField = models.BooleanField(default=False)
    display_name: models.CharField = models.CharField(verbose_name=_("Display name"),
                                                      max_length=30, help_text=_("Will be shown alongside entries"),
                                                      null=True)
    year_of_birth: models.PositiveIntegerField = models.PositiveIntegerField(verbose_name=_("Year of birth"),
                                                                             validators=[MinValueValidator(1900)],
                                                                             null=True, blank=True)
    post_code: models.ForeignKey = models.ForeignKey(PostCode, null=True, on_delete=models.SET_NULL)
    avatar: models.ForeignKey = models.ForeignKey(UserAvatar, null=True, on_delete=models.SET_NULL)
    editor: models.BooleanField = models.BooleanField(default=False)  # is this user an editor
    organisation: models.ForeignKey = models.ForeignKey(Organisation, default=None, null=True,
                                                        on_delete=models.SET_NULL)

    class Meta:
        ordering: List[str] = ['display_name']


    @property
    def user_slug(self) -> Optional[str]:
        # TODO merge with .util import user_to_slug avoiding circular input
        return f"{str(self.display_name).replace(' ', '-')}-{str(self.pk)}".lower()

    # to redirect to account profile page
    # def get_absolute_url(self) -> str:
    # suffix = f"{self.display_name}{self.pk}"
    # return reverse('profile_view')
    # return reverse('user_detail', args=[suffix])

    def __str__(self) -> str:
        return f"{self.email}"


def new_chat() -> int:  # required because a plain Chat.objects.create or a lambda can't be serialised for migrations :(
    c = Chat()
    c.save()
    return c.id


class UserPair(models.Model):
    user1: models.ForeignKey = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='first_user')
    user2: models.ForeignKey = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='second_user')
    chat: models.ForeignKey = models.ForeignKey(Chat, null=True, on_delete=models.SET_NULL,
                                                default=new_chat)  # I'm guessing that if for some reason a chat is deleted, that means we want to purge it and replace it with a new one

    def save(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        # ensure that there won't be two UserPairs created for one pair of users
        if self.user1.uuid > self.user2.uuid:
            swp = self.user1.uuid
            self.user1.uuid = self.user2.uuid
            self.user2.uuid = swp
        return super().save(*args, **kwargs)  # pyre-ignore[6] destructuring arguments
