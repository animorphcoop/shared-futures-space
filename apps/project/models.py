# pyre-strict

from django.db import models
from modelcluster.models import ClusterableModel
from django.utils import timezone
from django.utils.text import slugify

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from userauth.models import CustomUser # pyre-ignore[21]
from messaging.models import Chat # pyre-ignore[21]
from messaging.util import send_system_message # pyre-ignore[21]
from poll.models import SingleChoicePoll # pyre-ignore[21]
from area.models import Area # pyre-ignore[21]
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
    poll: models.ForeignKey = models.ForeignKey(SingleChoicePoll, null = True, default = None, on_delete = models.SET_NULL)

class PlanStage(models.Model):
    general_chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT, related_name = 'plan_general_chat')
    funding_chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT, related_name = 'plan_funding_chat')
    location_chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT, related_name = 'plan_location_chat')
    dates_chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT, related_name = 'plan_dates_chat')
    general_poll: models.ForeignKey = models.ForeignKey('poll.SingleChoicePoll', default = None, null = True, on_delete = models.SET_DEFAULT, related_name = 'plan_general_poll')
    funding_poll: models.ForeignKey = models.ForeignKey('poll.SingleChoicePoll', default = None, null = True, on_delete = models.SET_DEFAULT, related_name = 'plan_funding_poll')
    location_poll: models.ForeignKey = models.ForeignKey('poll.SingleChoicePoll', default = None, null = True, on_delete = models.SET_DEFAULT, related_name = 'plan_location_poll')
    dates_poll: models.ForeignKey = models.ForeignKey('poll.SingleChoicePoll', default = None, null = True, on_delete = models.SET_DEFAULT, related_name = 'plan_dates_poll')

class ActStage(models.Model):
    general_chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT, related_name = 'act_general_chat')
    funding_chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT, related_name = 'act_funding_chat')
    location_chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT, related_name = 'act_location_chat')
    dates_chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT, related_name = 'act_dates_chat')
    general_poll: models.ForeignKey = models.ForeignKey('poll.SingleChoicePoll', default = None, null = True, on_delete = models.SET_DEFAULT, related_name = 'act_general_poll')
    funding_poll: models.ForeignKey = models.ForeignKey('poll.SingleChoicePoll', default = None, null = True, on_delete = models.SET_DEFAULT, related_name = 'act_funding_poll')
    location_poll: models.ForeignKey = models.ForeignKey('poll.SingleChoicePoll', default = None, null = True, on_delete = models.SET_DEFAULT, related_name = 'act_location_poll')
    dates_poll: models.ForeignKey = models.ForeignKey('poll.SingleChoicePoll', default = None, null = True, on_delete = models.SET_DEFAULT, related_name = 'act_dates_poll')

class ReflectStage(models.Model):
    chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT)
    # feedback?

# PROJECTS

class ProjectMembership(models.Model):
    project: models.ForeignKey = models.ForeignKey('project.Project', on_delete=models.CASCADE)
    user: models.ForeignKey = models.ForeignKey('userauth.CustomUser', on_delete=models.CASCADE)
    owner: models.BooleanField = models.BooleanField(default = False)
    champion: models.BooleanField = models.BooleanField(default = False)

class ProjectTag(TaggedItemBase):
    content_object = ParentalKey('project.Project', on_delete=models.CASCADE, related_name='tagged_items')

def get_default_other_area() -> int:
    # this is bad, instead should not need a default but should specify every time a project is created
    return Area.objects.get_or_create(name='Other')[0].pk

class Project(ClusterableModel):
    class Stage(models.TextChoices):
        ENVISION = 'envision'
        PLAN = 'plan'
        ACT = 'act'
        REFLECT = 'reflect'
    slug: models.CharField = models.CharField(max_length=100, default='')
    name: models.CharField = models.CharField(max_length=100)
    description: models.CharField = models.CharField(max_length=2000)
    area: models.ForeignKey = models.ForeignKey(Area, on_delete = models.CASCADE, default = get_default_other_area) # TODO this is a bad default which should be replaced by forcing an area to be provided on creation
    tags = ClusterTaggableManager(through=ProjectTag, blank=True)
    envision_stage: models.ForeignKey = models.ForeignKey(EnvisionStage, null = True, default = None, on_delete = models.SET_NULL)
    plan_stage: models.ForeignKey = models.ForeignKey(PlanStage, null = True, default = None, on_delete = models.SET_NULL)
    act_stage: models.ForeignKey = models.ForeignKey(ActStage, null = True, default = None, on_delete = models.SET_NULL)
    reflect_stage: models.ForeignKey = models.ForeignKey(ReflectStage, null = True, default = None, on_delete = models.SET_NULL)
    current_stage: models.CharField = models.CharField(choices = Stage.choices, max_length = 8, null = True, default = None)
    def save(self, *args: List[Any], **kwargs: Dict[str,Any]) -> None:
        super().save(*args, **kwargs) # save first or we won't have an id
        if (self.slug == ''):
            self.slug = slugify(self.name + str(self.id)) # pyre-ignore[16]
        super().save() # without args because they tell it that it's the first time saving
    def start_envision(self) -> None:
        if self.current_stage is None:
            self.current_stage = self.Stage.ENVISION
            self.envision_stage = EnvisionStage.objects.create()
            self.save()
    def start_plan(self) -> None:
        if self.current_stage == self.Stage.ENVISION:
            self.current_stage = self.Stage.PLAN
            self.plan_stage = PlanStage.objects.create()
            # for testing purposes ONLY # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            self.plan_stage.general_poll = SingleChoicePoll.objects.create(question = 'general question', options = ['1', 'b'], expires = timezone.now() + timezone.timedelta(days=30))   #
            self.plan_stage.general_poll.make_votes(self)
            self.plan_stage.funding_poll = SingleChoicePoll.objects.create(question = 'funding question', options = ['1', 'b'], expires = timezone.now() + timezone.timedelta(days=30))   #
            self.plan_stage.funding_poll.make_votes(self)
            self.plan_stage.location_poll = SingleChoicePoll.objects.create(question = 'location question', options = ['1', 'b'], expires = timezone.now() + timezone.timedelta(days=30)) #
            self.plan_stage.location_poll.make_votes(self)
            self.plan_stage.dates_poll = SingleChoicePoll.objects.create(question = 'dates question', options = ['1', 'b'], expires = timezone.now() + timezone.timedelta(days=30))       #
            self.plan_stage.dates_poll.make_votes(self)
            self.plan_stage.general_poll.closed = True    #
            self.plan_stage.general_poll.save()
            self.plan_stage.funding_poll.closed = True    #
            self.plan_stage.funding_poll.save()
            self.plan_stage.location_poll.closed = True   #
            self.plan_stage.location_poll.save()
            self.plan_stage.dates_poll.closed = True      #
            self.plan_stage.dates_poll.save()
            self.plan_stage.save()
            self.save()
    def start_act(self) -> None:
        if self.current_stage == self.Stage.PLAN:
            if (self.plan_stage.general_poll is None or not self.plan_stage.general_poll.closed or
                self.plan_stage.funding_poll is None or not self.plan_stage.funding_poll.closed or
                self.plan_stage.location_poll is None or not self.plan_stage.location_poll.closed or
                self.plan_stage.dates_poll is None or not self.plan_stage.dates_poll.closed):
                raise ValueError('plan stage is not finished!')
            self.current_stage = self.Stage.ACT
            self.act_stage = ActStage.objects.create()
            self.act_stage.general_poll = SingleChoicePoll.objects.create(question = 'was this done?', options = ['yes', 'no'], expires = timezone.now() + timezone.timedelta(days=30)) # expiry date needs adjustment? TODO
            self.act_stage.general_poll.make_votes(self)
            send_system_message(self.act_stage.general_chat, 'poll', context_poll = self.plan_stage.general_poll)
            send_system_message(self.act_stage.general_chat, 'poll', context_poll = self.act_stage.general_poll)
            self.act_stage.funding_poll = SingleChoicePoll.objects.create(question = 'was this done?', options = ['yes', 'no'], expires = timezone.now() + timezone.timedelta(days=30)) # expiry date needs adjustment? TODO
            self.act_stage.funding_poll.make_votes(self)
            send_system_message(self.act_stage.funding_chat, 'poll', context_poll = self.plan_stage.funding_poll)
            send_system_message(self.act_stage.funding_chat, 'poll', context_poll = self.act_stage.funding_poll)
            self.act_stage.location_poll = SingleChoicePoll.objects.create(question = 'was this done?', options = ['yes', 'no'], expires = timezone.now() + timezone.timedelta(days=30)) # expiry date needs adjustment? TODO
            self.act_stage.location_poll.make_votes(self)
            send_system_message(self.act_stage.location_chat, 'poll', context_poll = self.plan_stage.location_poll)
            send_system_message(self.act_stage.location_chat, 'poll', context_poll = self.act_stage.location_poll)
            self.act_stage.dates_poll = SingleChoicePoll.objects.create(question = 'was this done?', options = ['yes', 'no'], expires = timezone.now() + timezone.timedelta(days=30)) # expiry date needs adjustment? TODO
            self.act_stage.dates_poll.make_votes(self)
            send_system_message(self.act_stage.dates_chat, 'poll', context_poll = self.plan_stage.dates_poll)
            send_system_message(self.act_stage.dates_chat, 'poll', context_poll = self.act_stage.dates_poll)
            self.act_stage.save()
            self.save()
    def start_reflect(self) -> None:
        if self.current_stage == self.Stage.ACT:
            self.current_stage = self.Stage.REFLECT
            self.reflect_stage = ReflectStage.objects.create()
            self.save()





