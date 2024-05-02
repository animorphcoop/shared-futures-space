import os
from os.path import isdir, splitext


from PIL import Image

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage, FileSystemStorage
from django import forms
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect
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
from remix.forms import (
    StartIdeaLocationStep,
    StartIdeaTitleAndDescriptionStep,
    StartIdeaImagesStep,
    CreateRemixForm,
    UpdateRemixForm,
)
from remix.models import RemixIdea, RemixBackgroundImage, Remix
from remix.three_models import list_three_models
from sfs import settings


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
