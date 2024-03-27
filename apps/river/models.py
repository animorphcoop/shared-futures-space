from typing import Any, Dict, List

from area.models import Area
from core.utils.tags_declusterer import tag_cluster_to_list
from django.contrib.gis.db.models import PointField
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from messaging.models import Chat
from messaging.util import send_system_message
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase

from apps.core.utils.slugifier import generate_random_string


def new_chat() -> (
    int
):  # required because a plain Chat.objects.create or a lambda can't be serialised for migrations :(
    c = Chat()
    c.save()
    return c.id


# STAGES
# stages are defined before projects because projects reference stages


class EnvisionStage(models.Model):
    class Step(models.TextChoices):
        GET_TO_KNOW = "1", "get to know"
        FINALISE_VISION = "2", "finalise vision"
        REVIEW = "3", "review tags and image"

    general_chat: models.ForeignKey = models.ForeignKey(
        Chat, default=new_chat, on_delete=models.SET_DEFAULT
    )
    step: models.CharField = models.CharField(
        max_length=1, choices=Step.choices, default=Step.GET_TO_KNOW
    )
    general_poll: models.ForeignKey = models.ForeignKey(
        "poll.SingleChoicePoll", null=True, default=None, on_delete=models.SET_NULL
    )

    def get_chat(self, topic: str) -> Chat:
        if topic == "general":
            return self.general_chat
        # no others


class PlanStage(models.Model):
    general_chat: models.ForeignKey = models.ForeignKey(
        Chat,
        default=new_chat,
        on_delete=models.SET_DEFAULT,
        related_name="plan_general_chat",
    )
    money_chat: models.ForeignKey = models.ForeignKey(
        Chat,
        default=new_chat,
        on_delete=models.SET_DEFAULT,
        related_name="plan_money_chat",
    )
    place_chat: models.ForeignKey = models.ForeignKey(
        Chat,
        default=new_chat,
        on_delete=models.SET_DEFAULT,
        related_name="plan_place_chat",
    )
    time_chat: models.ForeignKey = models.ForeignKey(
        Chat,
        default=new_chat,
        on_delete=models.SET_DEFAULT,
        related_name="plan_time_chat",
    )
    general_poll: models.ForeignKey = models.ForeignKey(
        "poll.SingleChoicePoll",
        default=None,
        null=True,
        on_delete=models.SET_DEFAULT,
        related_name="plan_general_poll",
    )
    money_poll: models.ForeignKey = models.ForeignKey(
        "poll.SingleChoicePoll",
        default=None,
        null=True,
        on_delete=models.SET_DEFAULT,
        related_name="plan_money_poll",
    )
    place_poll: models.ForeignKey = models.ForeignKey(
        "poll.SingleChoicePoll",
        default=None,
        null=True,
        on_delete=models.SET_DEFAULT,
        related_name="plan_place_poll",
    )
    time_poll: models.ForeignKey = models.ForeignKey(
        "poll.SingleChoicePoll",
        default=None,
        null=True,
        on_delete=models.SET_DEFAULT,
        related_name="plan_time_poll",
    )

    def get_chat(self, topic: str) -> Chat:
        if topic == "general":
            return self.general_chat
        elif topic == "money":
            return self.money_chat
        elif topic == "place":
            return self.place_chat
        elif topic == "time":
            return self.time_chat


class ActStage(models.Model):
    general_chat: models.ForeignKey = models.ForeignKey(
        Chat,
        default=new_chat,
        on_delete=models.SET_DEFAULT,
        related_name="act_general_chat",
    )
    money_chat: models.ForeignKey = models.ForeignKey(
        Chat,
        default=new_chat,
        on_delete=models.SET_DEFAULT,
        related_name="act_money_chat",
    )
    place_chat: models.ForeignKey = models.ForeignKey(
        Chat,
        default=new_chat,
        on_delete=models.SET_DEFAULT,
        related_name="act_place_chat",
    )
    time_chat: models.ForeignKey = models.ForeignKey(
        Chat,
        default=new_chat,
        on_delete=models.SET_DEFAULT,
        related_name="act_time_chat",
    )
    general_poll: models.ForeignKey = models.ForeignKey(
        "poll.SingleChoicePoll",
        default=None,
        null=True,
        on_delete=models.SET_DEFAULT,
        related_name="act_general_poll",
    )
    money_poll: models.ForeignKey = models.ForeignKey(
        "poll.SingleChoicePoll",
        default=None,
        null=True,
        on_delete=models.SET_DEFAULT,
        related_name="act_money_poll",
    )
    place_poll: models.ForeignKey = models.ForeignKey(
        "poll.SingleChoicePoll",
        default=None,
        null=True,
        on_delete=models.SET_DEFAULT,
        related_name="act_place_poll",
    )
    time_poll: models.ForeignKey = models.ForeignKey(
        "poll.SingleChoicePoll",
        default=None,
        null=True,
        on_delete=models.SET_DEFAULT,
        related_name="act_time_poll",
    )

    def get_chat(self, topic: str) -> Chat:
        if topic == "general":
            return self.general_chat
        elif topic == "money":
            return self.money_chat
        elif topic == "place":
            return self.place_chat
        elif topic == "time":
            return self.time_chat


class ReflectStage(models.Model):
    general_chat: models.ForeignKey = models.ForeignKey(
        Chat, default=new_chat, on_delete=models.SET_DEFAULT
    )
    general_poll: models.ForeignKey = models.ForeignKey(
        "poll.MultipleChoicePoll", default=None, null=True, on_delete=models.SET_DEFAULT
    )

    def get_chat(self, topic: str) -> Chat:
        if topic == "general":
            return self.general_chat
        # no others


# PROJECTS


class RiverMembership(models.Model):
    river: models.ForeignKey = models.ForeignKey(
        "river.River", on_delete=models.CASCADE
    )
    user: models.ForeignKey = models.ForeignKey(
        "userauth.CustomUser", on_delete=models.CASCADE
    )
    starter: models.BooleanField = models.BooleanField(default=False)
    join_date: models.DateField = models.DateField(default=timezone.now)

    def __str__(self):
        return f"User({str(self.user.uuid)}) membership to River({self.river.slug})"


class RiverTag(TaggedItemBase):
    content_object = ParentalKey(
        "river.River", on_delete=models.CASCADE, related_name="tagged_items"
    )


def get_default_other_area() -> int:
    # this is bad, instead should not need a default but should specify every time a river is created
    return Area.objects.get_or_create(name="Other")[0].pk


class River(ClusterableModel):
    class Stage(models.TextChoices):
        ENVISION = "envision"
        PLAN = "plan"
        ACT = "act"
        REFLECT = "reflect"
        FINISHED = "finished"

    slug: models.CharField = models.CharField(max_length=100, default="")
    started_on: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    title: models.CharField = models.CharField(max_length=100)
    description: models.CharField = models.CharField(max_length=2000)
    tags = ClusterTaggableManager(through=RiverTag, blank=True)
    image: models.ImageField = models.ImageField(upload_to="rivers/images/", blank=True)
    location = PointField(geography=True, srid=4326, null=True)
    location_exact = models.BooleanField(default=True)
    area: models.ForeignKey = models.ForeignKey(
        Area, on_delete=models.CASCADE, default=get_default_other_area
    )  # this is a bad default but can't really be replaced because it's used in every river creation, just immediately replaced, and it's a pain to change
    envision_stage: models.ForeignKey = models.ForeignKey(
        EnvisionStage, null=True, default=None, on_delete=models.SET_NULL
    )
    plan_stage: models.ForeignKey = models.ForeignKey(
        PlanStage, null=True, default=None, on_delete=models.SET_NULL
    )
    act_stage: models.ForeignKey = models.ForeignKey(
        ActStage, null=True, default=None, on_delete=models.SET_NULL
    )
    reflect_stage: models.ForeignKey = models.ForeignKey(
        ReflectStage, null=True, default=None, on_delete=models.SET_NULL
    )
    current_stage: models.CharField = models.CharField(
        choices=Stage.choices, max_length=8, null=True, default=None
    )

    @property
    def get_current_stage_string(self) -> str:
        stage_switch = {
            "envision": "Stage 1: Envision",
            "plan": "Stage 2: Plan",
            "act": "Stage 3: Act",
            "reflect": "Stage 4: Reflect",
            "finished": "Finished",
        }
        return stage_switch.get(self.current_stage, "")

    @property
    def get_started_months_ago(self) -> int:
        return timezone.now().month - self.started_on.month

    @property
    def tag_list(self):
        if not hasattr(self.tags, "all"):
            return self.tags
        return tag_cluster_to_list(self.tags)

    def save(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        super().save(*args, **kwargs)  # save first or we won't have an id
        if self.slug == "":
            title_slug = slugify(self.title)
            random_string = generate_random_string()
            self.slug = title_slug + "-" + random_string
        super().save()  # without args because they tell it that it's the first time saving

    def start_envision(self) -> None:
        if self.current_stage is None:
            self.current_stage = self.Stage.ENVISION
            self.envision_stage = EnvisionStage.objects.create()
            send_system_message(
                kind="salmon_envision_start",
                chat=self.envision_stage.general_chat,
                context_river=self,
            )

            """
            send_system_message(kind='salmon_envision_intro', chat=self.envision_stage.general_chat,context_river=self)
            send_system_message(kind='salmon_envision_swimmers', chat=self.envision_stage.general_chat,context_river=self)
            send_system_message(kind='salmon_envision_poll', chat=self.envision_stage.general_chat,context_river=self)
            """
            send_system_message(
                kind="salmon_wizard",
                chat=self.envision_stage.general_chat,
                context_river=self,
                text="I am the Salmon of Knowledge! I will help you navigate the river of your project.",
            )
            send_system_message(
                kind="salmon_wizard",
                chat=self.envision_stage.general_chat,
                context_river=self,
                text="Once 3 swimmers have joined the river, you can shape the vision together. Discuss the current description and make sure it captures your collective vision for this project.",
            )
            send_system_message(
                kind="salmon_wizard",
                chat=self.envision_stage.general_chat,
                context_river=self,
                text="When you’re ready, the river starter can launch a poll using the poll icon. Here they can edit the original description to include any changes that have been discussed. If the poll passes, you will move to the planning stage.",
            )
            self.save()

    def start_plan(self) -> None:
        pass

        if self.current_stage == self.Stage.ENVISION:
            self.current_stage = self.Stage.PLAN
            self.plan_stage = PlanStage.objects.create()
            self.plan_stage.save()
            send_system_message(
                kind="salmon_wizard",
                chat=self.plan_stage.general_chat,
                context_river=self,
                text="Welcome to the plan stage, here you can discuss and make plans for how you'll achieve your vision. The general tab is a space to talk about anything not covered in the other tabs.",
            )

            send_system_message(
                kind="salmon_wizard",
                chat=self.plan_stage.general_chat,
                context_river=self,
                text="To progress to the act stage, agree on your plans by passing polls in each of the money, place, and time chats. Once those have passed, the river starter can open a final poll in the general tab. If the general poll passes, you will move to the act stage.",
            )
            send_system_message(
                kind="salmon_wizard",
                chat=self.plan_stage.money_chat,
                context_river=self,
                text="How much will it cost to acheive your vision? Who is creating the budget? Do you need to apply for funding? The money tab is a place to discuss all finance related aspects of your river.",
            )
            send_system_message(
                kind="salmon_wizard",
                chat=self.plan_stage.place_chat,
                context_river=self,
                text="Where will your project take place? Do you need to get permission? Who's going to book the venue? The place tab is a place to discuss all location-based aspects of your river.",
            )
            send_system_message(
                kind="salmon_wizard",
                chat=self.plan_stage.time_chat,
                context_river=self,
                text="Are there any deadlines you need to meet? What date will you be working towards? Are there opening times you need to factor in? The time tab is a place to discuss all time related aspects of your river.",
            )

            self.save()

    def make_plan_general_poll(self) -> None:
        from poll.models import SingleChoicePoll

        ps = self.plan_stage
        ps.general_poll = SingleChoicePoll.objects.create(
            question="Are the money, place and time plans satisfactory?",
            expires=timezone.now() + timezone.timedelta(days=7),
            options=["yes", "no"],
            river=self,
        )
        ps.save()

    def start_act(self) -> None:
        from poll.models import SingleChoicePoll

        if self.current_stage == self.Stage.PLAN:
            """
            if (self.plan_stage.general_poll is None or not self.plan_stage.general_poll.closed or
                    self.plan_stage.money_poll is None or not self.plan_stage.money_poll.closed or
                    self.plan_stage.place_poll is None or not self.plan_stage.place_poll.closed or
                    self.plan_stage.time_poll is None or not self.plan_stage.time_poll.closed):
                # for testing purposes ONLY # # # # # # # # # # # # # # # # # # # # # # # # #

                self.plan_stage.general_poll = SingleChoicePoll.objects.create(question='general question',
                                                                               options=['1', 'b'],
                                                                               expires=timezone.now() + timezone.timedelta(
                                                                                   days=7),  #
                                                                               river=self)
                self.plan_stage.money_poll = SingleChoicePoll.objects.create(question='money question',
                                                                             options=['1', 'b'],
                                                                             expires=timezone.now() + timezone.timedelta(
                                                                                 days=7),  #
                                                                             river=self)
                self.plan_stage.place_poll = SingleChoicePoll.objects.create(question='place question',
                                                                             options=['1', 'b'],
                                                                             expires=timezone.now() + timezone.timedelta(
                                                                                 days=7),  #
                                                                             river=self)
                self.plan_stage.time_poll = SingleChoicePoll.objects.create(question='time question',
                                                                            options=['1', 'b'],
                                                                            expires=timezone.now() + timezone.timedelta(
                                                                                days=7),  #
                                                                            river=self)

                self.plan_stage.general_poll.closed = True  #
                self.plan_stage.general_poll.save()
                self.plan_stage.money_poll.closed = True  #
                self.plan_stage.money_poll.save()
                self.plan_stage.place_poll.closed = True  #
                self.plan_stage.place_poll.save()
                self.plan_stage.time_poll.closed = True  #
                self.plan_stage.time_poll.save()
            """
            # raise ValueError('plan stage is not finished!')

            self.current_stage = self.Stage.ACT
            self.act_stage = ActStage.objects.create()

            send_system_message(
                kind="salmon_wizard",
                chat=self.act_stage.general_chat,
                context_river=self,
                text="Time to act! You can share updates on how the plans are being carried out as you go, to document the flow, and discuss any changes that arise.",
            )

            send_system_message(
                kind="salmon_wizard",
                chat=self.act_stage.general_chat,
                context_river=self,
                text="As each aspect of the project concludes, you can use the polls in each tab to record this. When all polls have passed, you will progress to the reflect stage.",
            )

            if not self.location:
                send_system_message(
                    kind="salmon_wizard",
                    chat=self.act_stage.general_chat,
                    context_river=self,
                    # TODO: write/rewrite/confirm this message (https://op.animorph.coop/wp/840)
                    text="There is no location set yet, if you are a river starter using the settings menu to set a location",
                )

            send_system_message(
                kind="salmon_wizard",
                chat=self.act_stage.money_chat,
                context_river=self,
                text="Are the finances going according to plan? Are you over- or under-budget? Share and discuss money-related updates here.",
            )
            send_system_message(
                kind="salmon_wizard",
                chat=self.act_stage.place_chat,
                context_river=self,
                text="How is the space shaping up? Do you need to change location? Share and discuss place-related updates here.",
            )
            send_system_message(
                kind="salmon_wizard",
                chat=self.act_stage.time_chat,
                context_river=self,
                text="Is everything running on time? Are you overcoming any delays? Share and discuss time-related updates here.",
            )

            self.act_stage.general_poll = SingleChoicePoll.objects.create(
                question="Are all your actions complete?",
                options=["yes", "no"],
                expires=timezone.now() + timezone.timedelta(days=7),
                river=self,
            )

            # send_system_message(self.act_stage.general_chat, 'poll', context_poll=self.act_stage.general_poll)
            self.act_stage.money_poll = SingleChoicePoll.objects.create(
                question="Are all money-related actions done?",
                options=["yes", "no"],
                expires=timezone.now() + timezone.timedelta(days=7),
                river=self,
            )
            # send_system_message(self.act_stage.money_chat, 'poll', context_poll=self.act_stage.money_poll)
            self.act_stage.place_poll = SingleChoicePoll.objects.create(
                question="Are all place-related actions done?",
                options=["yes", "no"],
                expires=timezone.now() + timezone.timedelta(days=7),
                river=self,
            )
            # send_system_message(self.act_stage.place_chat, 'poll', context_poll=self.act_stage.place_poll)
            self.act_stage.time_poll = SingleChoicePoll.objects.create(
                question="Are all time-related actions done?",
                options=["yes", "no"],
                expires=timezone.now() + timezone.timedelta(days=7),
                river=self,
            )
            # send_system_message(self.act_stage.time_chat, 'poll', context_poll=self.act_stage.time_poll)
            self.act_stage.save()

            self.save()

    def start_reflect(self) -> None:
        from itertools import chain

        from django.db.models import Q
        from poll.models import MultipleChoicePoll
        from resources.models import CaseStudy, HowTo

        if self.current_stage == self.Stage.ACT:
            self.current_stage = self.Stage.REFLECT
            self.reflect_stage = ReflectStage.objects.create()
            self.save()
            self.reflect_stage.general_poll = MultipleChoicePoll.objects.create(
                question="Which of these resources did you find useful?",
                options=list(
                    dict.fromkeys(
                        chain(
                            *[
                                list(
                                    chain(
                                        HowTo.objects.filter(
                                            Q(tags__name__icontains=tag_a)
                                            | Q(tags__name__icontains=tag_b)
                                        ).values_list("title", flat=True),
                                        CaseStudy.objects.filter(
                                            Q(tags__name__icontains=tag_a)
                                            | Q(tags__name__icontains=tag_b)
                                        ).values_list("title", flat=True),
                                    )
                                )
                                for tag_a in self.tags.names()
                                for tag_b in self.tags.names()
                                if tag_a != tag_b and tag_a > tag_b
                            ]
                        )
                    )
                ),
                expires=timezone.now() + timezone.timedelta(days=7),
                river=self,
            )
            send_system_message(
                kind="salmon_wizard",
                chat=self.reflect_stage.general_chat,
                context_river=self,
                text="Welcome to the reflect stage! I trust your visions have become realities. You can reflect together here on what went well and would could have gone better, to create a record for yourselves and others to learn from. You can also track which, if any, of the resources I offered on this river were helpful to you. Congratulations on making it to the end of the river!",
            )
            self.reflect_stage.save()

    def finish(self) -> None:
        print(self)
        self.current_stage = self.Stage.FINISHED
        self.save()
