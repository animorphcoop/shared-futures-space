from typing import Any, Dict, List, Optional
from uuid import uuid4

from area.models import PostCode
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from messaging.models import Chat, new_chat


class Organisation(models.Model):
    uuid: models.UUIDField = models.UUIDField(default=uuid4)
    name: models.CharField = models.CharField(max_length=100)
    link: models.URLField = models.URLField()

    def __str__(self) -> str:
        return self.name


class UserAvatar(models.Model):
    avatar: models.ImageField = models.ImageField(
        upload_to="profile/avatars/", max_length=100, null=True, blank=True
    )

    @property
    def image_url(self) -> Optional[str]:
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url


class CustomUser(AbstractUser):
    uuid: models.UUIDField = models.UUIDField(default=uuid4, editable=False)
    first_name: None = None
    last_name: None = None
    email = models.EmailField(_("email address"), blank=True, unique=True)
    signup_date: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    added_data: models.BooleanField = models.BooleanField(default=False)
    display_name: models.CharField = models.CharField(
        verbose_name=_("Display name"),
        max_length=30,
        help_text=_("Will be shown alongside entries"),
        null=True,
    )
    year_of_birth: models.PositiveIntegerField = models.PositiveIntegerField(
        verbose_name=_("Year of birth"),
        validators=[MinValueValidator(1900)],
        null=True,
        blank=True,
    )
    post_code: models.ForeignKey = models.ForeignKey(
        PostCode, null=True, on_delete=models.SET_NULL
    )
    avatar: models.ForeignKey = models.ForeignKey(
        UserAvatar, null=True, on_delete=models.SET_NULL
    )
    editor: models.BooleanField = models.BooleanField(
        default=False
    )  # is this user an editor
    organisation: models.ForeignKey = models.ForeignKey(
        Organisation, default=None, null=True, on_delete=models.SET_NULL
    )
    postcode_changes: models.IntegerField = models.IntegerField(default=3)

    was_active: models.BooleanField = models.BooleanField(default=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # this just lets us use createsuperuser

    class Meta:
        ordering: List[str] = ["display_name"]

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


class UserPair(models.Model):
    user1: models.ForeignKey = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="first_user"
    )
    user2: models.ForeignKey = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="second_user"
    )
    chat: models.ForeignKey = models.ForeignKey(
        Chat, null=True, on_delete=models.SET_NULL, default=new_chat
    )  # I'm guessing that if for some reason a chat is deleted, that means we want to purge it and replace it with a new one
    blocked: models.BooleanField = models.BooleanField(default=False)

    def save(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        # ensure that there won't be two UserPairs created for one pair of users
        if self.user1.uuid > self.user2.uuid:
            swp = self.user1.uuid
            self.user1.uuid = self.user2.uuid
            self.user2.uuid = swp
        return super().save(*args, **kwargs)

    def block_user(self, user) -> None:
        from messaging.util import send_system_message

        Block.objects.create(user_pair=self, blocked_by=user)
        send_system_message(kind="blocked user", chat=self.chat, context_user_a=user)
        self.blocked = True
        self.save()


class Block(models.Model):
    timestamp: models.DateTimeField = models.DateTimeField(default=timezone.now)
    user_pair: models.ForeignKey = models.ForeignKey(UserPair, on_delete=models.CASCADE)
    blocked_by: models.ForeignKey = models.ForeignKey(
        "userauth.CustomUser", on_delete=models.SET_NULL, null=True
    )
