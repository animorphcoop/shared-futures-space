from itertools import chain
from typing import Any, Dict, List, Tuple
from uuid import UUID

from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.forms import ChoiceField, ModelChoiceField, ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from messaging.util import send_system_message
from river.models import River, RiverMembership

from .models import (
    BasePoll,
    BaseVote,
    MultipleChoicePoll,
    MultipleVote,
    SingleChoicePoll,
    SingleVote,
)


class PollView(TemplateView):
    template_name = "poll/poll_view.html"

    def post(self, request: WSGIRequest, uuid: UUID) -> HttpResponse:
        poll = BasePoll.objects.get(uuid=uuid)
        if hasattr(poll, "multiplechoicepoll"):
            poll = poll.multiplechoicepoll
        elif hasattr(poll, "singlechoicepoll"):
            poll = poll.singlechoicepoll
        if (
            request.user.is_active
            and not poll.check_closed()
            and "choice" in request.POST
            and BaseVote.objects.filter(user=request.user, poll=poll).exists()
        ):
            try:
                choice = poll.options.index(request.POST["choice"]) + 1
            except ValueError:
                choice = 0
            if hasattr(poll, "multiplechoicepoll"):
                v = MultipleVote.objects.get(poll=poll, user=request.user)
                if choice in v.choice:
                    v.choice.remove(choice)
                else:
                    v.choice.append(choice)
                v.save()
            elif hasattr(poll, "singlechoicepoll"):
                SingleVote.objects.filter(poll=poll, user=request.user).update(
                    choice=choice
                )
            poll.check_closed()
            if poll.check_closed() and "slug" in request.POST:
                # adding 'just_finished' so frontend can refresh, did not want to tamper with request payload
                return self.render_to_response(
                    self.get_context_data(
                        uuid=uuid, request=request, just_finished="true"
                    )
                )
        return self.render_to_response(
            self.get_context_data(uuid=uuid, request=request)
        )

    def get_context_data(
        self, uuid: UUID, **kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:  # adding request and just_finished as optional causes errors
        ctx = super().get_context_data(**kwargs)
        poll = BasePoll.objects.get(uuid=uuid)
        if hasattr(poll, "multiplechoicepoll"):
            poll = poll.multiplechoicepoll
        elif hasattr(poll, "singlechoicepoll"):
            poll = poll.singlechoicepoll
        ctx["poll"] = poll
        ctx["poll_name"] = poll.question
        ctx["poll_description"] = poll.description
        ctx["poll_votes_cast"] = len(list(chain(*poll.current_results.values())))
        ctx["poll_total_votes"] = len(BaseVote.objects.filter(poll=poll))
        total_votes_uncast = ctx["poll_total_votes"] - ctx["poll_votes_cast"]
        second_most_votes_cast = sorted(
            [len(votes) for votes in poll.current_results.values()], reverse=True
        )[1]
        ctx["poll_results"] = [
            (
                option,
                votes,
                len(votes) + 1 > second_most_votes_cast + total_votes_uncast - 1,
            )
            for option, votes in poll.current_results.items()
        ]
        for result in ctx["poll_results"]:
            for user in result[1]:
                user.join_date = RiverMembership.objects.get(
                    user=user, river=poll.river
                ).join_date
        ctx["any_threshold"] = False
        for _, _, threshold in ctx["poll_results"]:
            if threshold:
                ctx["any_threshold"] = True
        ctx["poll_closed"] = poll.check_closed()
        ctx["poll_expires"] = poll.expires
        ctx["poll_results_winners"] = get_winners(list(poll.current_results.items()))

        # added the variable to htmx response when the poll closes so frontend can refresh
        # ctx['just_finished']

        # river slug for htmx to run conditional check if the poll is closed so to trigger refreshing on the frontend
        river = poll.river
        ctx["slug"] = river.slug
        ctx["river_stage"] = river.current_stage
        ctx["starters"] = RiverMembership.objects.filter(
            river=river, starter=True
        ).values_list(
            "user__id", flat=True
        )  # for telling whether we should show the edit poll button
        return ctx


def get_winners(
    options: List[Tuple[str, List[Any]]], winners: List[Tuple[str, List[Any]]] = []
) -> List[str]:
    # get a list of equally-most-highly voted results, in case of a draw
    if len(options) == 0:
        return list(map(lambda pair: pair[0], winners))
    else:
        current_max = len(winners[0][1]) if len(winners) > 0 else 0
        if len(options[0][1]) > current_max:
            return get_winners(options[1:], [options[0]])
        elif len(options[0][1]) == current_max:
            return get_winners(options[1:], winners + [options[0]])
        else:
            return get_winners(options[1:], winners)


class PollCreateForm(ModelForm):
    river = ModelChoiceField(
        queryset=River.objects.all()
    )  # should only be projects you're a member of
    kind = ChoiceField(
        choices=[("SINGLE", "single-choice"), ("MULTIPLE", "multiple-choice")]
    )

    class Meta:
        model = SingleChoicePoll
        fields = ["question", "description", "options", "expires"]


class PollCreateView(CreateView):
    template_name = "poll/poll_create.html"
    model = SingleChoicePoll
    form_class = PollCreateForm

    def form_valid(self, form) -> HttpResponseRedirect:
        # print(form.cleaned_data)
        if form.cleaned_data["kind"] == "SINGLE":
            new_poll = SingleChoicePoll.objects.create(
                question=form.cleaned_data["question"],
                description=form.cleaned_data["description"],
                options=form.instance.options,
                expires=form.instance.expires,
                created_by=self.request.user,
                river=form.cleaned_data["river"],
            )
        elif form.cleaned_data["kind"] == "MULTIPLE":
            new_poll = MultipleChoicePoll.objects.create(
                question=form.cleaned_data["question"],
                description=form.cleaned_data["description"],
                options=form.instance.options,
                expires=form.instance.expires,
                created_by=self.request.user,
                river=form.cleaned_data["river"],
            )
        return HttpResponseRedirect(reverse("poll_view", args=[new_poll.uuid]))

    def get_success_url(self) -> str:
        return reverse("poll_view", args=[self.object.uuid])


def poll_edit(request: WSGIRequest) -> HttpResponse:
    # update description of the (old) poll, return new description for htmx
    old_poll = BasePoll.objects.get(uuid=request.POST["poll-uuid"])
    if old_poll.closed:
        raise PermissionDenied("poll is closed")

    river_membership = RiverMembership.objects.get(
        user=request.user, river=old_poll.river
    )
    if not river_membership.starter:
        raise PermissionDenied(
            "User is not authorised to edit the poll - non-riverstarter"
        )

    river, stage, topic = old_poll.get_poll_context(old_poll)
    send_system_message(stage.get_chat(topic), "poll_edited", context_poll=old_poll)
    new_poll = SingleChoicePoll.objects.create(
        question=old_poll.question,
        description=request.POST["new-description"],
        options=old_poll.options,
        expires=old_poll.expires,
        created_by=old_poll.created_by,
        river=old_poll.river,
    )
    if topic == "general":
        stage.general_poll = new_poll
    elif topic == "money":
        stage.money_poll = new_poll
    elif topic == "place":
        stage.place_poll = new_poll
    elif topic == "time":
        stage.time_poll = new_poll

    old_poll.closed = True
    old_poll.save()

    stage.save()
    return HttpResponseRedirect(reverse("poll_view", args=[new_poll.uuid]))
