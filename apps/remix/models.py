from uuid import uuid4

from django.utils import timezone
from django.contrib.gis.db.models import PointField
from django.db import models
from django.db.models.fields import UUIDField, CharField
from django.db.models.fields.files import ImageField
from django.db.models.fields.related import ForeignKey
from django.urls import reverse

from messaging.models import Chat, new_chat


class RemixIdea(models.Model):
    """The initial idea, it's chat, and all the remixes"""

    uuid = models.UUIDField(default=uuid4, editable=False)
    user = models.ForeignKey("userauth.CustomUser", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=2000)
    location = PointField(geography=True, srid=4326, null=True)
    chat = models.ForeignKey(Chat, default=new_chat, on_delete=models.SET_DEFAULT)

    def get_absolute_url(self):
        return reverse("remix_idea", kwargs={"uuid": self.uuid})

    @property
    def marker(self):
        from map.markers import idea_marker

        return idea_marker(self)

    @property
    def image_url(self):
        # First preference, a remix snapshot
        last_remix_with_snapshot = (
            self.remixes.exclude(snapshot="").order_by("created_at").first()
        )
        if last_remix_with_snapshot:
            return last_remix_with_snapshot.snapshot.url

        # Otherwise, any background image, preference for initial images
        background_image = self.background_images.order_by("-initial_image").first()
        if background_image:
            return background_image.image.url


class RemixBackgroundImage(models.Model):
    """A background for the remix scene"""

    uuid = models.UUIDField(default=uuid4, editable=False)
    image = models.ImageField(upload_to="remix/backgrounds/")
    idea = models.ForeignKey(
        RemixIdea, related_name="background_images", on_delete=models.CASCADE
    )
    initial_image = models.BooleanField(default=False)
    from_message: models.ForeignKey = models.ForeignKey(
        "messaging.Message", null=True, on_delete=models.SET_NULL
    )


class Remix(models.Model):
    """A remix!"""

    created_at = models.DateTimeField(default=timezone.now)
    uuid = models.UUIDField(default=uuid4, editable=False)
    idea = models.ForeignKey(
        RemixIdea, related_name="remixes", on_delete=models.CASCADE
    )
    user = models.ForeignKey("userauth.CustomUser", on_delete=models.CASCADE)
    background_image = models.ForeignKey(
        RemixBackgroundImage, related_name="background_image", on_delete=models.CASCADE
    )
    scene = models.JSONField(null=True)
    snapshot = models.ImageField(upload_to="remix/snapshots/", blank=True)
    from_remix = models.ForeignKey("remix.Remix", null=True, on_delete=models.SET_NULL)

    def get_absolute_url(self):
        return reverse("remix", kwargs={"uuid": self.uuid})
