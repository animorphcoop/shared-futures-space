# pyre-strict

from django.db import models
from modelcluster.models import ClusterableModel
from django.utils import timezone

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

# STAGES
# stages are defined before projects because projects reference stages

class EnvisionStage(models.Model):
    class Step(models.TextChoices):
        GET_TO_KNOW = '1', 'get to know'
        FINALISE_VISION = '2', 'finalise vision'
        REVIEW = '3', 'review tags and image'
    chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT)
    step: models.CharField = models.CharField(max_length = 1, choices = Step.choices, default = Step.GET_TO_KNOW)

class PlanStage(models.Model):
    general_chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT, related_name = 'plan_general_chat')
    funding_chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT, related_name = 'plan_funding_chat')
    location_chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT, related_name = 'plan_location_chat')
    dates_chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT, related_name = 'plan_dates_chat')
    general_poll: models.ForeignKey = models.ForeignKey('poll.Poll', default = None, null = True, on_delete = models.SET_DEFAULT, related_name = 'plan_general_poll')
    funding_poll: models.ForeignKey = models.ForeignKey('poll.Poll', default = None, null = True, on_delete = models.SET_DEFAULT, related_name = 'plan_funding_poll')
    location_poll: models.ForeignKey = models.ForeignKey('poll.Poll', default = None, null = True, on_delete = models.SET_DEFAULT, related_name = 'plan_location_poll')
    dates_poll: models.ForeignKey = models.ForeignKey('poll.Poll', default = None, null = True, on_delete = models.SET_DEFAULT, related_name = 'plan_dates_poll')

class ActStage(models.Model):
    general_chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT, related_name = 'act_general_chat')
    funding_chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT, related_name = 'act_funding_chat')
    location_chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT, related_name = 'act_location_chat')
    dates_chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT, related_name = 'act_dates_chat')
    general_poll: models.ForeignKey = models.ForeignKey('poll.Poll', default = None, null = True, on_delete = models.SET_DEFAULT, related_name = 'act_general_poll')
    funding_poll: models.ForeignKey = models.ForeignKey('poll.Poll', default = None, null = True, on_delete = models.SET_DEFAULT, related_name = 'act_funding_poll')
    location_poll: models.ForeignKey = models.ForeignKey('poll.Poll', default = None, null = True, on_delete = models.SET_DEFAULT, related_name = 'act_location_poll')
    dates_poll: models.ForeignKey = models.ForeignKey('poll.Poll', default = None, null = True, on_delete = models.SET_DEFAULT, related_name = 'act_dates_poll')

class ReflectStage(models.Model):
    chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT)
    # feedback?

# PROJECTS

class ProjectTag(TaggedItemBase):
    content_object = ParentalKey('project.Project', on_delete=models.CASCADE, related_name='tagged_items')

class Project(ClusterableModel):
    class Stage(models.TextChoices):
        ENVISION = 'envision'
        PLAN = 'plan'
        ACT = 'act'
        REFLECT = 'reflect'
    slug: models.CharField = models.CharField(max_length=100, default='')
    name: models.CharField = models.CharField(max_length=200)
    description: models.CharField = models.CharField(max_length=2000)
    tags = ClusterTaggableManager(through=ProjectTag, blank=True)
    envision_stage: models.ForeignKey = models.ForeignKey(EnvisionStage, null = True, default = None, on_delete = models.SET_NULL)
    plan_stage: models.ForeignKey = models.ForeignKey(PlanStage, null = True, default = None, on_delete = models.SET_NULL)
    act_stage: models.ForeignKey = models.ForeignKey(ActStage, null = True, default = None, on_delete = models.SET_NULL)
    reflect_stage: models.ForeignKey = models.ForeignKey(ReflectStage, null = True, default = None, on_delete = models.SET_NULL)
    current_stage: models.CharField(choices = Stage.choices)
    def save(self, *args: List[Any], **kwargs: Dict[str,Any]) -> None:
        if (self.slug == ''):
            self.slug = quote(self.name)[:86] + shake_256(str(self.id).encode()).hexdigest(8) # pyre-ignore[16] same
        return super().save(*args, **kwargs)
    def start_envision(self):
        self.current_stage = Stage.ENVISION
        self.envision_stage = EnvisionStage.objects.create()
    def start_plan(self):
        self.current_stage = Stage.PLAN
        self.plan_stage = PlanStage.objects.create()
    def start_act(self):
        self.current_stage = Stage.ACT
        self.act_stage = ActStage.objects.create()
        # put polls in chats

class ProjectMembership(models.Model):
    project: models.ForeignKey = models.ForeignKey(Project, on_delete=models.CASCADE)
    user: models.ForeignKey = models.ForeignKey('userauth.CustomUser', on_delete=models.CASCADE)
    owner: models.BooleanField = models.BooleanField(default = False)
    champion: models.BooleanField = models.BooleanField(default = False)





