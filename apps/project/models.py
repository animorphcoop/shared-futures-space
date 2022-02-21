# pyre-strict

from django.db import models
from userauth.models import CustomUser # pyre-ignore[21]
from messaging.models import Chat # pyre-ignore[21]
from urllib.parse import quote
from hashlib import shake_256

from typing import List, Dict, Any

class Idea(models.Model):
    slug = models.CharField(max_length=100, default='')
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    proposed_by = models.ForeignKey('userauth.CustomUser', null=True, on_delete=models.SET_NULL) # null=true means nullable
    def save(self, *args: List[Any], **kwargs: Dict[str,Any]) -> None:
        if (self.slug == ''):
            self.slug = quote(self.name)[:86] + shake_256(str(self.id).encode()).hexdigest(8) # pyre-ignore[6,8,16] thinks CharField can't be used as a str
        return super().save(*args, **kwargs)

class IdeaSupport(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE)
    user = models.ForeignKey('userauth.CustomUser', on_delete=models.CASCADE)

# ---

def new_chat() -> int: # required because a plain Chat.objects.create or a lambda can't be serialised for migrations :(
    c = Chat()
    c.save()
    return c.id

class Project(models.Model):
    slug = models.CharField(max_length=100, default='')
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    chat = models.ForeignKey('messaging.Chat', null = True, on_delete = models.SET_NULL, default=new_chat) # I'm guessing that if for some reason a chat is deleted, that means we want to purge it and replace it with a new one
    def save(self, *args: List[Any], **kwargs: Dict[str,Any]) -> None:
        if (self.slug == ''): # shouldn't happen because created from ideas with existing slugs, but just in case
            self.slug = quote(self.name)[:86] + shake_256(str(self.id).encode()).hexdigest(8) # pyre-ignore[6,8,16] same
        return super().save(*args, **kwargs)

class ProjectMembership(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey('userauth.CustomUser', on_delete=models.CASCADE)
    owner = models.BooleanField(default = False)
    champion = models.BooleanField(default = False)
