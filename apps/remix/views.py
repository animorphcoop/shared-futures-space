import os
from os.path import isdir, splitext


from PIL import Image

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage, FileSystemStorage
from django import forms
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import (
    TemplateView,
    FormView,
    CreateView,
    DetailView,
    UpdateView,
)
from django.views.generic.edit import ModelFormMixin
from formtools.wizard.views import SessionWizardView, NamedUrlSessionWizardView

from core.forms import SharedFuturesWizardView
from dashboard.forms import AreaForm
from map.markers import idea_marker
from messaging.models import Message
from messaging.views import ChatView, ChatUpdateCheck
from remix.forms import (
    StartIdeaLocationStep,
    StartIdeaTitleAndDescriptionStep,
    StartIdeaImagesStep,
    CreateRemixForm,
    UpdateRemixForm,
)
from remix.models import RemixIdea, RemixBackgroundImage, Remix
from remix.three_models import list_three_models
from river.models import River
from sfs import settings
from userauth.util import get_system_user


class RemixMapView(TemplateView):
    template_name = "remix/map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["home"] = None

        if self.request.user.is_authenticated:
            area = self.request.user.post_code.area
            if area.location:
                context["home"] = {
                    "center": area.location.coords,
                    "zoom": area.zoom,
                }

        ideas = RemixIdea.objects.all()

        markers = []
        for idea in ideas:
            marker = idea_marker(idea)
            if marker:
                markers.append(marker)

        context["markers"] = markers
        return context


class RemixIdeaStartWizardView(LoginRequiredMixin, SharedFuturesWizardView):
    template_name = "remix/start_idea_wizard.html"

    form_list = [
        StartIdeaLocationStep,
        StartIdeaTitleAndDescriptionStep,
        StartIdeaImagesStep,
    ]

    # This storage will temporarily store the uploaded files for the wizard
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "tmp"))

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        form = self.form_list[step]
        if form == StartIdeaLocationStep and self.request.user.is_authenticated:
            kwargs["current_user"] = self.request.user
        return kwargs

    def done(self, form_list, **kwargs):
        """Merge data from all the forms and create the idea

        Form data is already validated by this point, so we don't need to recheck it.
        """

        cleaned_data = {}
        images = None
        for form in form_list:
            if isinstance(form, StartIdeaImagesStep):
                images = form.files.values()
            else:
                cleaned_data.update(form.cleaned_data)
        idea = RemixIdea.objects.create(user=self.request.user, **cleaned_data)
        if images:
            for image in images:
                background_image = RemixBackgroundImage.objects.create(
                    idea=idea, image=image
                )
                with Image.open(background_image.image.file) as img:
                    width, height = img.size
                    target_aspect_ratio = 16 / 9
                    aspect_ratio = width / height
                    if aspect_ratio > target_aspect_ratio:
                        # wider than 16/9
                        # need to modify width
                        new_width = target_aspect_ratio * height
                        offset = int(abs(width - new_width) / 2)
                        cropped = img.crop([offset, 0, width - offset, height])
                        cropped.save(background_image.image.path)
                    elif aspect_ratio < target_aspect_ratio:
                        # taller than 16 / 9
                        # need to modify height
                        new_height = width / target_aspect_ratio
                        offset = int(abs(new_height - height) / 2)
                        cropped = img.crop([0, offset, width, height - offset])
                        cropped.save(background_image.image.path)
        return redirect(idea)


class RemixIdeaView(DetailView):
    template_name = "remix/idea.html"
    model = RemixIdea

    # TODO: maybe include a slug, from the title?
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["remixes"] = self.object.remixes.exclude(snapshot="")
        return context


class RemixIdeaChatView(ChatView):
    template_name = "remix/chat.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        request = self.request

        idea = get_object_or_404(RemixIdea, uuid=kwargs["uuid"])
        chat = idea.chat

        # TODO: fix blatant lie! it's any registered user.. but can't include all those
        # Adding the request user ensures this user can post messages...
        members = [request.user]

        message_list = Message.objects.all().filter(chat=chat).order_by("timestamp")

        pagination_data = self.paginate_messages(request, message_list)

        context.update(
            {
                "chat_ref": chat,
                "members": members,
                "system_user": get_system_user(),
                "page_obj": pagination_data["page_obj"],
                "page_number": pagination_data["page_number"],
                "messages_displayed_count": pagination_data["messages_displayed_count"],
                "messages_left_count": pagination_data["messages_left_count"],
                "message_post_url": reverse("remix_idea_chat", args=[idea.uuid]),
                "message_count_url": reverse(
                    "remix_idea_chat_message_count", args=[idea.uuid]
                ),
                "message_list_url": reverse(
                    "remix_idea_chat_message_list", args=[idea.uuid]
                ),
                "unique_id": idea.uuid,
                "chat_open": True,
            }
        )

        return context


class RemixIdeaChatMessageListView(RemixIdeaChatView):
    pass


class RemixIdeaChatUpdateView(DetailView):
    model = RemixIdea

    # TODO: maybe include a slug, from the title?
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def render_to_response(self, context, **response_kwargs):
        chat = self.object.chat
        message_list = Message.objects.all().filter(chat=chat).order_by("timestamp")
        return HttpResponse(message_list.count())


class RemixView(DetailView):
    template_name = "remix/remix.html"
    model = Remix

    # TODO: maybe include a slug, from the title?
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["models"] = list_three_models()
        return context


class CreateRemixView(View):
    def post(self, request: WSGIRequest):
        form = CreateRemixForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            remix = form.save()
            return redirect(remix)
        # failure is not an option!
        raise ValidationError("could not create remix!")


class UpdateRemixView(ModelFormMixin, View):
    model = Remix
    form_class = UpdateRemixForm

    def post(self, request: WSGIRequest, pk=None):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            remix = form.save()
            return redirect(remix.idea)  # we go back to the idea
        # failure is not an option!
        raise ValidationError("could not update remix!")
