# pyre-strict

from django.db import models
from modelcluster.models import ClusterableModel

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from userauth.models import CustomUser # pyre-ignore[21]
from messaging.models import Chat # pyre-ignore[21]
from urllib.parse import quote
from hashlib import shake_256

from typing import List, Dict, Any

def new_chat() -> int: # required because a plain Chat.objects.create or a lambda can't be serialised for migrations :(
    c = Chat()
    c.save()
    return c.id

class ProjectTag(TaggedItemBase):
    content_object = ParentalKey('project.Project', on_delete=models.CASCADE, related_name='tagged_items')

class Project(ClusterableModel):
    slug: models.CharField = models.CharField(max_length=100, default='')
    name: models.CharField = models.CharField(max_length=200)
    description: models.CharField = models.CharField(max_length=2000)
    tags = ClusterTaggableManager(through=ProjectTag, blank=True)
    chat: models.ForeignKey = models.ForeignKey('messaging.Chat', null = True, on_delete = models.SET_DEFAULT, default=new_chat) # I'm guessing that if for some reason a chat is deleted, that means we want to purge it and replace it with a new one
    def save(self, *args: List[Any], **kwargs: Dict[str,Any]) -> None:
        if (self.slug == ''):
            self.slug = quote(self.name)[:86] + shake_256(str(self.id).encode()).hexdigest(8) # pyre-ignore[16] same
        return super().save(*args, **kwargs)

class ProjectMembership(models.Model):
    project: models.ForeignKey = models.ForeignKey(Project, on_delete=models.CASCADE)
    user: models.ForeignKey = models.ForeignKey('userauth.CustomUser', on_delete=models.CASCADE)
    owner: models.BooleanField = models.BooleanField(default = False)
    champion: models.BooleanField = models.BooleanField(default = False)
