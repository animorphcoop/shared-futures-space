from typing import Dict, List, Union
from uuid import uuid4

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from userauth.models import CustomUser


class BaseVote(models.Model):
    user: models.ForeignKey = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    poll: models.ForeignKey = models.ForeignKey(
        "poll.BasePoll", on_delete=models.CASCADE
    )


class SingleVote(BaseVote):
    choice: models.IntegerField = models.IntegerField(null=True, default=None)

    def clean(self) -> None:
        cleaned_data = super().clean()
        # 0 indicates the always-present unask-the-question option
        if self.choice < 0 or self.choice > len(self.poll.options):
            raise ValidationError(
                "not a valid choice for that poll (got "
                + str(self.choice)
                + ", expected an integer in 0 - "
                + str(len(self.poll.options))
                + ")"
            )
        else:
            return cleaned_data


class MultipleVote(BaseVote):
    choice: ArrayField = ArrayField(models.IntegerField())


def validate_poll_options(value: List[str]) -> bool:
    if type(value) == list and all(map(lambda x: type(x) == str, value)):
        return True
    else:
        raise ValidationError(
            "poll options must be a list of strings (got " + repr(value) + ")"
        )


class BasePoll(models.Model):
    uuid: models.UUIDField = models.UUIDField(default=uuid4)
    question: models.CharField = models.CharField(max_length=100, default="")
    description: models.CharField = models.CharField(
        max_length=2000, default=""
    )  # description must be long enough to include the full text of any river description
    options: models.JSONField = models.JSONField(validators=[validate_poll_options])
    expires: models.DateTimeField = models.DateTimeField()
    created: models.DateTimeField = models.DateTimeField(default=timezone.now)
    closed: models.BooleanField = models.BooleanField(default=False)
    when_closed: models.DateTimeField = models.DateTimeField(null=True, default=None)
    passed: models.BooleanField = models.BooleanField(default=False)
    vote_kind: models.Model = BaseVote
    invalid_option: models.BooleanField = models.BooleanField(default=False)
    created_by: models.ForeignKey = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, default=0
    )
    river: models.ForeignKey = models.ForeignKey(
        "river.River", on_delete=models.CASCADE
    )

    @property
    def specific(self) -> Union["SingleChoicePoll", "MultipleChoicePoll"]:
        if hasattr(self, "multiplechoicepoll"):
            return self.multiplechoicepoll
        else:
            return self.singlechoicepoll

    def close(self) -> None:
        from messaging.util import send_system_message

        self.when_closed = timezone.now()
        if hasattr(self, "singlechoicepoll"):
            river, stage, topic = self.get_poll_context(self.singlechoicepoll)
            if river:
                # this poll is the current poll of the active stage of a river
                if (
                    sorted(
                        self.current_results.items(), key=lambda x: x[1], reverse=True
                    )[0][0]
                    == "yes"
                ):
                    # poll has passed
                    self.passed = True
                    self.save()
                    if river.current_stage == river.Stage.ENVISION:
                        river.start_plan()
                        river.description = self.description
                        river.save()
                        send_system_message(
                            kind="finished_envision",
                            chat=river.envision_stage.general_chat,
                            context_river=river,
                        )
                    elif river.current_stage == river.Stage.PLAN:
                        if (
                            topic == "general"
                            and river.plan_stage.money_poll
                            and river.plan_stage.money_poll.passed
                            and river.plan_stage.place_poll
                            and river.plan_stage.place_poll.passed
                            and river.plan_stage.time_poll
                            and river.plan_stage.time_poll.passed
                        ):
                            river.start_act()
                            river.save()
                        elif (
                            topic != "general"
                            and river.plan_stage.money_poll
                            and river.plan_stage.money_poll.passed
                            and river.plan_stage.place_poll
                            and river.plan_stage.place_poll.passed
                            and river.plan_stage.time_poll
                            and river.plan_stage.time_poll.passed
                        ):
                            river.make_plan_general_poll()
                    elif river.current_stage == river.Stage.ACT:
                        if (
                            river.act_stage.general_poll
                            and river.act_stage.general_poll.passed
                            and river.plan_stage.money_poll
                            and river.plan_stage.money_poll.passed
                            and river.act_stage.place_poll
                            and river.plan_stage.place_poll.passed
                            and river.plan_stage.time_poll
                            and river.act_stage.time_poll.passed
                        ):
                            river.start_reflect()
                            river.save()
                    elif (
                            topic != "general"
                            and river.act_stage.money_poll
                            and river.act_stage.money_poll.passed
                            and river.act_stage.place_poll
                            and river.act_stage.place_poll.passed
                            and river.act_stage.time_poll
                            and river.act_stage.time_poll.passed
                    ):
                            river.make_act_general_poll()

        elif hasattr(self, "multiplechoicepoll"):
            from river.models import ReflectStage, River

            rs = ReflectStage.objects.filter(general_poll=self)
            if rs.exists():
                river = River.objects.get(reflect_stage=rs[0])
                if river.current_stage == river.Stage.REFLECT:
                    river.finish()
                    river.save()

    def get_poll_context(self, poll):
        from river.models import ActStage, EnvisionStage, PlanStage, River

        es = EnvisionStage.objects.filter(general_poll=poll)
        if es.exists():
            return (River.objects.get(envision_stage=es[0]), es[0], "general")
        psg = PlanStage.objects.filter(general_poll=poll)
        if psg.exists():
            return (River.objects.get(plan_stage=psg[0]), psg[0], "general")
        psf = PlanStage.objects.filter(money_poll=poll)
        if psf.exists():
            return (River.objects.get(plan_stage=psf[0]), psf[0], "money")
        psl = PlanStage.objects.filter(place_poll=poll)
        if psl.exists():
            return (River.objects.get(plan_stage=psl[0]), psl[0], "place")
        psd = PlanStage.objects.filter(time_poll=poll)
        if psd.exists():
            return (River.objects.get(plan_stage=psd[0]), psd[0], "time")
        asg = ActStage.objects.filter(general_poll=poll)
        if asg.exists():
            return (River.objects.get(act_stage=asg[0]), asg[0], "general")
        asf = ActStage.objects.filter(money_poll=poll)
        if asf.exists():
            return (River.objects.get(act_stage=asf[0]), asf[0], "money")
        asl = ActStage.objects.filter(place_poll=poll)
        if asl.exists():
            return (River.objects.get(act_stage=asl[0]), asl[0], "place")
        asd = ActStage.objects.filter(time_poll=poll)
        if asd.exists():
            return (River.objects.get(act_stage=asd[0]), asd[0], "time")
        return False, False, False


class SingleChoicePoll(BasePoll):
    vote_kind = SingleVote

    @property
    def current_results(self) -> Dict[str, List[CustomUser]]:
        votes = SingleVote.objects.filter(poll=self, choice__isnull=False)
        results = {option: [] for option in self.options}
        if self.invalid_option:
            results["poll is wrong"] = []
            for vote in votes:
                results[
                    self.options[vote.choice - 1]
                    if vote.choice != 0
                    else "poll is wrong"
                ].append(vote.user)
        else:
            for vote in votes:
                results[self.options[vote.choice - 1]].append(vote.user)
        return results

    def check_closed(self) -> bool:
        if self.closed:
            return True
        elif self.expires < timezone.now():
            self.closed = True
            self.close()
            self.save()
            return True
        else:
            vote_nums = sorted(
                [
                    len(SingleVote.objects.filter(poll=self, choice=option))
                    for option in range(len(self.options) + 1)
                ],
                reverse=True,
            )
            if vote_nums[0] > vote_nums[1] + len(
                SingleVote.objects.filter(poll=self, choice__isnull=True)
            ):
                # if all remaining votes went to the current second-place option it still wouldn't equal the top option
                self.closed = True
                self.close()
                self.save()
                return True
            else:
                return False


class MultipleChoicePoll(BasePoll):
    vote_kind = MultipleVote

    @property
    def current_results(self) -> Dict[str, List[CustomUser]]:
        votes = MultipleVote.objects.filter(~models.Q(choice=[]), poll=self)
        results = {option: [] for option in self.options}
        if self.invalid_option:
            results["poll is wrong"] = []
            for vote in votes:
                for choice in vote.choice:
                    results[
                        self.options[choice - 1] if choice != 0 else "poll is wrong"
                    ].append(vote.user)
        else:
            for vote in votes:
                for choice in vote.choice:
                    results[self.options[choice - 1]].append(vote.user)
        return results

    def check_closed(self) -> bool:
        # doesn't check votes, because then how would it tell when the last person has finished voting?
        if self.closed:
            return True
        elif self.expires < timezone.now():
            self.close()
            self.save()
            return True
        else:
            return False


# initialise the votes relevant to this poll. needed so we know who's allowed to vote on it. should be called after creating any poll
@receiver(post_save, sender=SingleChoicePoll)
def make_votes_single(sender, instance, created, **kwargs) -> None:
    from river.models import RiverMembership

    if created:
        for voter in RiverMembership.objects.filter(river=instance.basepoll_ptr.river):
            instance.vote_kind.objects.create(
                user=voter.user, poll=instance, choice=None
            )


@receiver(post_save, sender=MultipleChoicePoll)
def make_votes_multiple(sender, instance, created, **kwargs) -> None:
    from river.models import RiverMembership

    if created:
        for voter in RiverMembership.objects.filter(river=instance.basepoll_ptr.river):
            instance.vote_kind.objects.create(user=voter.user, poll=instance, choice=[])
