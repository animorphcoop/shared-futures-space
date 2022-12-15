# pyre-strict

from django.db import models
from modelcluster.models import ClusterableModel
from django.utils import timezone
from django.utils.text import slugify

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from userauth.models import CustomUser  # pyre-ignore[21]
from messaging.models import Chat  # pyre-ignore[21]
from messaging.util import send_system_message  # pyre-ignore[21]
from area.models import Area  # pyre-ignore[21]
from urllib.parse import quote
from hashlib import shake_256

from typing import List, Dict, Any
from apps.core.utils.slugifier import generate_random_string


def new_chat() -> int:  # required because a plain Chat.objects.create or a lambda can't be serialised for migrations :(
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

    general_chat: models.ForeignKey = models.ForeignKey(Chat, default = new_chat, on_delete = models.SET_DEFAULT)
    step: models.CharField = models.CharField(max_length = 1, choices = Step.choices, default = Step.GET_TO_KNOW)
    general_poll: models.ForeignKey = models.ForeignKey('poll.SingleChoicePoll', null = True, default = None, on_delete = models.SET_NULL)

class PlanStage(models.Model):
    general_chat: models.ForeignKey = models.ForeignKey(Chat, default=new_chat, on_delete=models.SET_DEFAULT,
                                                        related_name='plan_general_chat')
    money_chat: models.ForeignKey = models.ForeignKey(Chat, default=new_chat, on_delete=models.SET_DEFAULT,
                                                        related_name='plan_money_chat')
    place_chat: models.ForeignKey = models.ForeignKey(Chat, default=new_chat, on_delete=models.SET_DEFAULT,
                                                         related_name='plan_place_chat')
    time_chat: models.ForeignKey = models.ForeignKey(Chat, default=new_chat, on_delete=models.SET_DEFAULT,
                                                      related_name='plan_time_chat')
    general_poll: models.ForeignKey = models.ForeignKey('poll.SingleChoicePoll', default=None, null=True,
                                                        on_delete=models.SET_DEFAULT, related_name='plan_general_poll')
    money_poll: models.ForeignKey = models.ForeignKey('poll.SingleChoicePoll', default=None, null=True,
                                                        on_delete=models.SET_DEFAULT, related_name='plan_money_poll')
    place_poll: models.ForeignKey = models.ForeignKey('poll.SingleChoicePoll', default=None, null=True,
                                                         on_delete=models.SET_DEFAULT,
                                                         related_name='plan_place_poll')
    time_poll: models.ForeignKey = models.ForeignKey('poll.SingleChoicePoll', default=None, null=True,
                                                      on_delete=models.SET_DEFAULT, related_name='plan_time_poll')


class ActStage(models.Model):
    general_chat: models.ForeignKey = models.ForeignKey(Chat, default=new_chat, on_delete=models.SET_DEFAULT,
                                                        related_name='act_general_chat')
    money_chat: models.ForeignKey = models.ForeignKey(Chat, default=new_chat, on_delete=models.SET_DEFAULT,
                                                        related_name='act_money_chat')
    place_chat: models.ForeignKey = models.ForeignKey(Chat, default=new_chat, on_delete=models.SET_DEFAULT,
                                                         related_name='act_place_chat')
    time_chat: models.ForeignKey = models.ForeignKey(Chat, default=new_chat, on_delete=models.SET_DEFAULT,
                                                      related_name='act_time_chat')
    general_poll: models.ForeignKey = models.ForeignKey('poll.SingleChoicePoll', default=None, null=True,
                                                        on_delete=models.SET_DEFAULT, related_name='act_general_poll')
    money_poll: models.ForeignKey = models.ForeignKey('poll.SingleChoicePoll', default=None, null=True,
                                                        on_delete=models.SET_DEFAULT, related_name='act_money_poll')
    place_poll: models.ForeignKey = models.ForeignKey('poll.SingleChoicePoll', default=None, null=True,
                                                         on_delete=models.SET_DEFAULT, related_name='act_place_poll')
    time_poll: models.ForeignKey = models.ForeignKey('poll.SingleChoicePoll', default=None, null=True,
                                                      on_delete=models.SET_DEFAULT, related_name='act_time_poll')


class ReflectStage(models.Model):
    general_chat: models.ForeignKey = models.ForeignKey(Chat, default=new_chat, on_delete=models.SET_DEFAULT)
    general_poll: models.ForeignKey = models.ForeignKey('poll.MultipleChoicePoll', default = None, null = True,
                                                        on_delete = models.SET_DEFAULT)

# PROJECTS

class RiverMembership(models.Model):
    river: models.ForeignKey = models.ForeignKey('river.River', on_delete=models.CASCADE)
    user: models.ForeignKey = models.ForeignKey('userauth.CustomUser', on_delete=models.CASCADE)
    starter: models.BooleanField = models.BooleanField(default=False)
    join_date: models.DateField = models.DateField(default = timezone.now)

class RiverTag(TaggedItemBase):
    content_object = ParentalKey('river.River', on_delete=models.CASCADE, related_name='tagged_items')


def get_default_other_area() -> int:
    # this is bad, instead should not need a default but should specify every time a river is created
    return Area.objects.get_or_create(name='Other')[0].pk


class River(ClusterableModel):
    class Stage(models.TextChoices):
        ENVISION = 'envision'
        PLAN = 'plan'
        ACT = 'act'
        REFLECT = 'reflect'
        FINISHED = 'finished'

    slug: models.CharField = models.CharField(max_length=100, default='')
    started_on: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    title: models.CharField = models.CharField(max_length=100)
    description: models.CharField = models.CharField(max_length=2000)
    tags = ClusterTaggableManager(through=RiverTag, blank=True)
    image: models.ImageField = models.ImageField(upload_to='rivers/images/', blank=True)
    area: models.ForeignKey = models.ForeignKey(Area, on_delete=models.CASCADE,
                                            default=get_default_other_area)  # this is a bad default but can't really be replaced because it's used in every river creation, just immediately replaced, and it's a pain to change
    envision_stage: models.ForeignKey = models.ForeignKey(EnvisionStage, null=True, default=None,
                                                          on_delete=models.SET_NULL)
    plan_stage: models.ForeignKey = models.ForeignKey(PlanStage, null=True, default=None, on_delete=models.SET_NULL)
    act_stage: models.ForeignKey = models.ForeignKey(ActStage, null=True, default=None, on_delete=models.SET_NULL)
    reflect_stage: models.ForeignKey = models.ForeignKey(ReflectStage, null=True, default=None,
                                                         on_delete=models.SET_NULL)
    current_stage: models.CharField = models.CharField(choices=Stage.choices, max_length=8, null=True, default=None)

    @property
    def get_current_stage_string(self) -> str:
        stage_switch = {
            "envision": 'Stage 1: Envision',
            "plan": 'Stage 2: Plan',
            "act": 'Stage 3: Act',
            "reflect": 'Stage 4: Reflect',
            "finished": 'Finished',
        }
        return stage_switch.get(self.current_stage, "")

    @property
    def get_started_months_ago(self) -> int:
        return timezone.now().month - self.started_on.month


    def save(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        super().save(*args, **kwargs)  # save first or we won't have an id
        if (self.slug == ''):
            title_slug = slugify(self.title)
            random_string = generate_random_string()
            self.slug = title_slug + "-" + random_string
        super().save()  # without args because they tell it that it's the first time saving

    def start_envision(self) -> None:
        if self.current_stage is None:
            self.current_stage = self.Stage.ENVISION
            self.envision_stage = EnvisionStage.objects.create()
            self.save()

    def start_plan(self) -> None:
        from poll.models import SingleChoicePoll # pyre-ignore[21]
        if self.current_stage == self.Stage.ENVISION:
            self.current_stage = self.Stage.PLAN
            self.plan_stage = PlanStage.objects.create()
            self.plan_stage.save()
            self.save()

    def make_plan_general_poll(self) -> None:
        from poll.models import SingleChoicePoll
        ps = self.plan_stage
        ps.general_poll = SingleChoicePoll.objects.create(question = 'Are the money, place and time plans satisfactory?', expires = timezone.now() + timezone.timedelta(days=3), options = ['yes', 'no'],
                                                          river = self)
        ps.save()

    def start_act(self) -> None:
        from poll.models import SingleChoicePoll
        if self.current_stage == self.Stage.PLAN:
            if (self.plan_stage.general_poll is None or not self.plan_stage.general_poll.closed or
                    self.plan_stage.money_poll is None or not self.plan_stage.money_poll.closed or
                    self.plan_stage.place_poll is None or not self.plan_stage.place_poll.closed or
                    self.plan_stage.time_poll is None or not self.plan_stage.time_poll.closed):
                # for testing purposes ONLY # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                self.plan_stage.general_poll = SingleChoicePoll.objects.create(question='general question',
                                                                           options=['1', 'b'],
                                                                           expires=timezone.now() + timezone.timedelta(
                                                                               days=3),  #
                                                                           river=self)
                self.plan_stage.money_poll = SingleChoicePoll.objects.create(question='money question',
                                                                           options=['1', 'b'],
                                                                           expires=timezone.now() + timezone.timedelta(
                                                                               days=3),  #
                                                                           river=self)
                self.plan_stage.place_poll = SingleChoicePoll.objects.create(question='place question',
                                                                            options=['1', 'b'],
                                                                            expires=timezone.now() + timezone.timedelta(
                                                                                days=3),  #
                                                                            river=self)
                self.plan_stage.time_poll = SingleChoicePoll.objects.create(question='time question', options=['1', 'b'],
                                                                         expires=timezone.now() + timezone.timedelta(
                                                                             days=3),  #
                                                                         river=self)
                self.plan_stage.general_poll.closed = True  #
                self.plan_stage.general_poll.save()
                self.plan_stage.money_poll.closed = True  #
                self.plan_stage.money_poll.save()
                self.plan_stage.place_poll.closed = True  #
                self.plan_stage.place_poll.save()
                self.plan_stage.time_poll.closed = True  #
                self.plan_stage.time_poll.save()
                #raise ValueError('plan stage is not finished!')
            self.current_stage = self.Stage.ACT
            self.act_stage = ActStage.objects.create()
            self.act_stage.general_poll = SingleChoicePoll.objects.create(question='was this done?',
                                                                          options=['yes', 'no'],
                                                                          expires=timezone.now() + timezone.timedelta(
                                                                              days=3),
                                                                          river=self)
            send_system_message(self.act_stage.general_chat, 'poll', context_poll=self.plan_stage.general_poll)
            send_system_message(self.act_stage.general_chat, 'poll', context_poll=self.act_stage.general_poll)
            self.act_stage.money_poll = SingleChoicePoll.objects.create(question='was this done?',
                                                                          options=['yes', 'no'],
                                                                          expires=timezone.now() + timezone.timedelta(
                                                                              days=3),
                                                                          river=self)
            send_system_message(self.act_stage.money_chat, 'poll', context_poll=self.plan_stage.money_poll)
            send_system_message(self.act_stage.money_chat, 'poll', context_poll=self.act_stage.money_poll)
            self.act_stage.place_poll = SingleChoicePoll.objects.create(question='was this done?',
                                                                           options=['yes', 'no'],
                                                                           expires=timezone.now() + timezone.timedelta(
                                                                               days=3),
                                                                           river=self)
            send_system_message(self.act_stage.place_chat, 'poll', context_poll=self.plan_stage.place_poll)
            send_system_message(self.act_stage.place_chat, 'poll', context_poll=self.act_stage.place_poll)
            self.act_stage.time_poll = SingleChoicePoll.objects.create(question='was this done?',
                                                                        options=['yes', 'no'],
                                                                        expires=timezone.now() + timezone.timedelta(
                                                                            days=3),
                                                                        river=self)
            send_system_message(self.act_stage.time_chat, 'poll', context_poll=self.plan_stage.time_poll)
            send_system_message(self.act_stage.time_chat, 'poll', context_poll=self.act_stage.time_poll)
            self.act_stage.save()
            self.save()

    def start_reflect(self) -> None:
        from resources.models import Resource, CaseStudy, HowTo # pyre-ignore[21]
        from poll.models import MultipleChoicePoll
        from django.db.models import Q
        from itertools import chain
        if self.current_stage == self.Stage.ACT:
            self.current_stage = self.Stage.REFLECT
            self.reflect_stage = ReflectStage.objects.create()
            self.save()
            self.reflect_stage.general_poll = MultipleChoicePoll.objects.create(question = 'Which of these resources did you find useful?',
                                                                                options = list(dict.fromkeys(chain(*[list(chain(HowTo.objects.filter(Q(tags__name__icontains=tag_a) | Q(tags__name__icontains=tag_b)).values_list('title', flat = True),
                                                                                CaseStudy.objects.filter(Q(tags__name__icontains=tag_a) | Q(tags__name__icontains=tag_b)).values_list('title', flat = True)))
                                                                                for tag_a in self.tags.names() for tag_b in self.tags.names() if tag_a != tag_b and tag_a > tag_b]))),
                                                                                expires = timezone.now() + timezone.timedelta(days=3),
                                                                                river = self)
            self.reflect_stage.save()

    def finish(self) -> None:
        print(self)
        print('11111111111')
        self.current_stage = self.Stage.FINISHED
        self.save()
