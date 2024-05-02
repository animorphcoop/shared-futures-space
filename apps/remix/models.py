from uuid import uuid4

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


class RemixBackgroundImage(models.Model):
    """A background for the remix scene"""

    uuid = models.UUIDField(default=uuid4, editable=False)
    image = models.ImageField(upload_to="remix/backgrounds/")
    idea = models.ForeignKey(
        RemixIdea, related_name="background_images", on_delete=models.CASCADE
    )


class Remix(models.Model):
    """A remix!"""

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

    def get_absolute_url(self):
        return reverse("remix", kwargs={"uuid": self.uuid})
