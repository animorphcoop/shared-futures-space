import os
from itertools import chain
from typing import Any, Dict, List, Type

from action.models import Action
from action.util import send_offer
from area.models import PostCode
from core.utils.tags_declusterer import tag_cluster_to_list
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.http.request import QueryDict
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic.base import ContextMixin, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from formtools.wizard.views import SessionWizardView
from messaging.forms import ChatForm
from messaging.util import send_system_message
from messaging.views import ChatUpdateCheck, ChatView
from poll.models import SingleChoicePoll
from resources.models import CaseStudy, HowTo
from userauth.util import get_userpair

from .forms import (
    CreateRiverFormStep1,
    CreateRiverFormStep2,
    CreateRiverFormStep3,
    RiverDescriptionUpdateForm,
    RiverImageUpdateForm,
    RiverLocationUpdateForm,
    RiverTitleUpdateForm,
)
from .models import River, RiverMembership


class RiverView(DetailView):
    template_name = "river.html"
    model = River

    def post(self, request: WSGIRequest, slug: str) -> HttpResponse:
        river = River.objects.get(slug=slug)
        if request.POST["action"] == "leave":
            membership = RiverMembership.objects.get(user=request.user, river=river)
            if (
                not membership.starter
            ):  # reject starter's attempting to leave, this is not supported by the interface - you should rescind ownership first, because you won't be allowed to if you're the last starter left.
                membership.delete()
                # if to notify for each, need to know the current river stage and post to general

        if request.POST["action"] == "join":
            if (
                len(RiverMembership.objects.filter(user=request.user, river=river)) == 0
                and request.user.post_code.area == river.area
            ):
                RiverMembership.objects.create(
                    user=request.user, river=river, starter=False
                )
                # if to notify for each, need to know the current river stage and post to general

                if len(RiverMembership.objects.filter(river=river)) == 3:
                    send_system_message(
                        kind="salmon_envision_poll_available",
                        chat=river.envision_stage.general_chat,
                        context_river=river,
                    )
        return super().get(request, slug)

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["starters"] = RiverMembership.objects.filter(
            river=context["object"].pk, starter=True
        )
        context["user"] = self.request.user
        context["slug"] = self.object.slug
        context["members"] = RiverMembership.objects.filter(river=context["object"].pk)
        context["resources"] = list(
            dict.fromkeys(
                chain(
                    *[
                        list(
                            chain(
                                HowTo.objects.filter(
                                    Q(tags__name__icontains=tag_a)
                                    | Q(tags__name__icontains=tag_b)
                                ),
                                CaseStudy.objects.filter(
                                    Q(tags__name__icontains=tag_a)
                                    | Q(tags__name__icontains=tag_b)
                                ),
                            )
                        )
                        for tag_a in self.object.tags.names()
                        for tag_b in self.object.tags.names()
                        if tag_a != tag_b and tag_a > tag_b
                    ]
                )
            )
        )  # ensure we don't have (tag1, tag2) and (tag2, tag1) searched separately. they would be filtered out by fromkeys but might as well remove earlier on
        context["object"].tags = tag_cluster_to_list(context["object"].tags)
        context["envision_locked"] = False
        context["plan_locked"] = context["object"].current_stage == River.Stage.ENVISION
        context["act_locked"] = (
            context["object"].current_stage == River.Stage.ENVISION
            or context["object"].current_stage == River.Stage.PLAN
        )
        context["reflect_locked"] = (
            context["object"].current_stage != River.Stage.REFLECT
        )
        return context


class EditRiverView(UpdateView):
    model = River
    fields = ["title", "description", "image"]

    def get(self, *args: List[Any], **kwargs: Dict[str, Any]) -> HttpResponse:
        # login_required is idempotent so we may as well apply it here in case it's forgotten in urls.py
        return login_required(super().get)(*args, **kwargs)

    def post(
        self, request: WSGIRequest, slug: str, **kwargs: Dict[str, Any]
    ) -> HttpResponse:
        # changing the river image - same code appears not to upload using put method
        river = River.objects.get(slug=slug)
        # print(request.body)
        form = RiverImageUpdateForm(request.POST, request.FILES, instance=river)
        if form.is_valid():
            form.full_clean()
            river.image = form.cleaned_data.get("image", None)
            river.save()
            context = {"river": river}
            return render(request, "river/partials/river-image.html", context)
        return HttpResponse(
            "Sorry, your description could not be processed, please refresh the page"
        )
        """
        # abdication currently disabled
        if (RiverMembership.objects.get(river=river, user=request.user).starter == True):
            if ('abdicate' in request.POST and request.POST['abdicate'] == 'abdicate'):
                starters = RiverMembership.objects.filter(river=river, starter=True)
                if (
                        len(starters) >= 2):  # won't be orphaning the river (TODO: allow rivers to be shut down, in which case they can be orphaned. v2?)
                    my_membership = RiverMembership.objects.get(river=river, user=request.user, starter=True)
                    my_membership.starter = False
                    my_membership.save()
                    print(
                        '!!! WARNING E !!! not sending a message to the river, because rivers no longer have one central chat. how to disseminate that information?')
                    # send_system_message(river.chat, 'lost_ownership', context_user_a = request.user)

            river.title = request.POST['title']
            river.description = request.POST['description']
            river.save()
        return redirect(reverse('view_river', args=[slug]))
        """

    # was able to pass the byte stream of image via put but impractical comparing to post so updating here only text and description
    def put(
        self,
        request: WSGIRequest,
        slug: str,
        *args: tuple[str, ...],
        **kwargs: dict[str, Any]
    ) -> HttpResponse:
        data = QueryDict(request.body).dict()

        if slug:
            river = River.objects.get(slug=slug)

            if data.get("title"):
                form = RiverTitleUpdateForm(data, instance=river)
                if form.is_valid():
                    river.title = form.cleaned_data.get("title")
                    river.save()
                    return HttpResponse(river.title)
                return HttpResponse(
                    "Sorry, your title could not be processed, please refresh the page"
                )

            elif data.get("description"):
                form = RiverDescriptionUpdateForm(data, instance=river)
                if form.is_valid():
                    river.description = form.cleaned_data.get("description")
                    river.save()
                    return HttpResponse(river.description)
                return HttpResponse(
                    "Sorry, your description could not be processed, please refresh the page"
                )
            elif data.get("location"):
                form = RiverLocationUpdateForm(data, instance=river)
                if form.is_valid():
                    river.location = form.cleaned_data.get("location")
                    river.save()
                    return HttpResponse(river.location)
                return HttpResponse(
                    "Sorry, your location could not be processed, please refresh the page"
                )

            else:
                return HttpResponse(
                    "Sorry, couldn't process your request, please refresh & try again."
                )

        else:
            return HttpResponse(
                "Sorry, couldn't process your request, please refresh & try again."
            )

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["starters"] = RiverMembership.objects.filter(
            river=context["object"], starter=True
        )
        context["members"] = RiverMembership.objects.filter(river=context["object"].pk)
        context["user"] = self.request.user
        return context


class ManageRiverView(TemplateView):
    def post(self, request: WSGIRequest, slug: str) -> HttpResponse:
        river = River.objects.get(slug=slug)
        membership = RiverMembership.objects.get(id=request.POST["membership"])
        # security checks
        if RiverMembership.objects.get(
            user=request.user, river=river
        ).starter == True and membership.river == River.objects.get(
            slug=slug
        ):  # since the form takes any uid
            if request.POST["action"] == "offer_starter":
                if not membership.starter:  # not an starter already
                    send_offer(
                        request.user,
                        membership.user,
                        "become_starter",
                        param_river=river,
                    )
                    # send_system_message(get_userpair(request.user, membership.user).chat,'lost_championship_notification', context_user_a=request.user,context_river=membership.river)
            membership.save()  # IMPORTANT: happens here because if membership.save is called after membership.delete, it reinstantiates a new identical membership. spent a while chasing that one.
            if request.POST["action"] == "remove_swimmer":
                if not membership.starter:
                    send_system_message(
                        get_userpair(request.user, membership.user).chat,
                        "removed_from_river",
                        context_user_a=request.user,
                        context_user_b=membership.user,
                        context_river=river,
                    )
                    membership.delete()

        return self.get(request, slug=slug)

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        river = River.objects.get(slug=kwargs["slug"])
        context["starters"] = RiverMembership.objects.filter(
            river=river.pk, starter=True
        )
        context["members"] = RiverMembership.objects.filter(river=river.pk)
        context["open_starter_offers"] = [
            member.user
            for member in context["members"]
            if Action.objects.filter(
                receiver=member.user,
                kind="become_starter",
                param_river=river,
                result=None,
            ).exists()
        ]
        context["slug"] = kwargs["slug"]
        return context


class RiverChatView(ChatView):
    form_class: Type[ChatForm] = ChatForm


class RiverChatMessageListView(ChatView):
    pass


class RiverChatUpdateView(ChatUpdateCheck):
    pass


class CreateRiverPollView(TemplateView):
    template_name = "create_river_poll.html"

    def post(
        self, request: WSGIRequest, slug: str, stage: str, topic: str
    ) -> HttpResponse:
        river = River.objects.get(slug=slug)
        if river.current_stage == stage:
            if river.current_stage == river.Stage.ENVISION:
                stage_ref = river.envision_stage
            elif river.current_stage == river.Stage.PLAN:
                stage_ref = river.plan_stage
            elif river.current_stage == river.Stage.ACT:
                stage_ref = river.act_stage
            elif river.current_stage == river.Stage.REFLECT:
                stage_ref = river.reflect_stage
            else:
                return HttpResponse(
                    "could not create poll, current stage not recognised ("
                    + stage
                    + ")"
                )
            if topic == "general":
                poll_ref = stage_ref.general_poll
            elif topic == "money":
                poll_ref = stage_ref.money_poll
            elif topic == "place":
                poll_ref = stage_ref.place_poll
            elif topic == "time":
                poll_ref = stage_ref.time_poll
            else:
                poll_ref = None
                return HttpResponse(
                    "could not create poll, topic not recognised (" + topic + ")"
                )
            if poll_ref is None or (poll_ref.closed and not poll_ref.passed):
                if "description" in request.POST:
                    try:
                        if stage == river.Stage.ENVISION:
                            question = "is this an acceptable vision?"
                        elif stage == river.Stage.PLAN:
                            question = "is this an acceptable plan for " + topic + "?"
                        elif stage == river.Stage.ACT:
                            question = "was the plan for " + topic + "carried out?"
                        elif stage == river.Stage.REFLECT:
                            question = "???"
                        else:
                            question = ""
                        poll = SingleChoicePoll.objects.create(
                            question=question,
                            description=request.POST["description"],
                            options=["yes", "no"],
                            invalid_option=False,
                            expires=timezone.now() + timezone.timedelta(days=7),
                            river=river,
                        )
                        if topic == "general":
                            stage_ref.general_poll = poll
                        elif topic == "money":
                            stage_ref.money_poll = poll
                        elif topic == "place":
                            stage_ref.place_poll = poll
                        elif topic == "time":
                            stage_ref.time_poll = poll
                        else:
                            return HttpResponse(
                                "could not create poll, topic not recognised ("
                                + topic
                                + ")"
                            )
                        stage_ref.save()
                        # send_system_message(chat=river.envision_stage.general_chat, kind='poll', context_poll=poll) current poll apppears at the bottom of the chat, not as part of it
                        return HttpResponseRedirect(
                            reverse("poll_view", args=[poll.uuid])
                        )
                    except Exception as e:
                        return HttpResponse(
                            "could not create poll, unknown error: " + str(e)
                        )
                else:
                    return HttpResponse(
                        "could not create poll, no description supplied"
                    )
            else:
                return HttpResponse(
                    "could not create poll, another poll is still not closed"
                )
        else:
            return HttpResponse("could not create poll, current stage is not " + stage)

    def get_context_data(self, slug: str, stage: str, topic: str) -> Dict[str, Any]:
        ctx = super().get_context_data()
        ctx["river"] = River.objects.get(slug=slug)
        ctx["slug"] = slug
        ctx["stage"] = stage
        ctx["topic"] = topic
        ctx["prompt"] = {
            "envision": "Describe the shared vision",
            "plan": "Describe the plan for " + topic,
            "act": "Describe what happened with " + topic,
        }[stage]
        ctx["default"] = {"envision": ctx["river"].description, "plan": "", "act": ""}[
            stage
        ]
        return ctx


class StageContextMixin(ContextMixin):
    def get_context_data(
        self, *args: List[Any], **kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        context = super().get_context_data(*args, **kwargs)
        river = get_object_or_404(River, slug=self.kwargs["slug"])
        context["river"] = river

        context["starters"] = river.rivermembership_set.filter(
            starter=True
        ).values_list("user", flat=True)

        context["is_member"] = (
            self.request.user.is_authenticated
            and river.rivermembership_set.filter(user=self.request.user).exists()
        )
        return context


class EnvisionView(StageContextMixin, TemplateView):
    template_name = "envision_view.html"


class PlanView(StageContextMixin, TemplateView):
    template_name = "plan_view.html"


class ActView(StageContextMixin, TemplateView):
    template_name = "act_view.html"


class ReflectView(StageContextMixin, TemplateView):
    template_name = "reflect_view.html"


class RiverStartWizardView(SessionWizardView):
    """A multistep form view for creating a river"""

    template_name = "start_river_wizard.html"
    form_list = [
        CreateRiverFormStep1,
        CreateRiverFormStep2,
        CreateRiverFormStep3,
    ]

    # This storage will temporarily store the uploaded files for the wizard
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "tmp"))

    def get(self, request, *args, **kwargs):
        """Support discard and restoring on get

        discard:
            if you add "?discard" to url it will clear storage
            and send you to dashboard

        restoring saved data:
            by default if you reload the form with a GET it'll
            reset the storage, we want to continue where we
            left off, so we treat it as a goto step

        to *not* reset storage if we just get the page again"""
        if "discard" in self.request.GET:
            self.storage.reset()
            return HttpResponseRedirect(reverse_lazy("dashboard"))

        return self.render_goto_step(self.steps.first)

    def render_goto_step(self, goto_step, **kwargs):
        """Save data when jumping to another step, e.g. previous step

        By default, jumping to a step does _not_ save the data for the page you are on.
        We override it to do so as suggested by the docs:

        See https://django-formtools.readthedocs.io/en/latest/wizard.html#formtools.wizard.views.WizardView.render_goto_step

        Inspired by https://stackoverflow.com/a/65099307

        Importantly, it does *not* validate the data when jumping to a step as we
        want to save the data regardless, e.g. when jumping back to the first page, we want to
        still save what was entered on the second page.

        (validation *does* happen when you do next/submit)
        """
        if self.steps.current != goto_step:
            """Only save data if we are actually moving steps

            They are the same if we resubmit the "go to step" form
            e.g. pressing refresh in the browser

            We need to avoid overwriting the storage in that scenario
            """
            form = self.get_form(
                data=self.request.POST,
                files=self.request.FILES,
            )

            self.storage.set_step_data(
                self.storage.current_step, self.process_step(form)
            )
            self.storage.set_step_files(
                self.storage.current_step,
                self.process_step_files(form),
            )

        return super().render_goto_step(goto_step, **kwargs)

    def done(self, form_list, **kwargs):
        """Merge data from all the forms and save/initialize the river

        Form data is already validated by this point, so we don't need to recheck it.
        """

        cleaned_data = {}
        for form in form_list:
            cleaned_data.update(form.cleaned_data)

        tags = cleaned_data.pop("tags", [])

        river = River(**cleaned_data)
        for tag in tags:
            river.tags.add(tag)

        try:
            post_code = PostCode.objects.all().filter(code=self.request.user.post_code)[
                0
            ]
            river.area = post_code.area
        except PostCode.DoesNotExist:
            pass

        river.save()
        river.start_envision()

        RiverMembership.objects.create(
            user=self.request.user, river=river, starter=True
        )

        return HttpResponseRedirect(reverse_lazy("view_river", args=[river.slug]))
