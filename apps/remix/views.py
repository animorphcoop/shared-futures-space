import os
from os.path import isdir, splitext


from PIL import Image

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage, FileSystemStorage
from django import forms
from django.shortcuts import redirect
from django.views.generic import TemplateView, FormView, CreateView, DetailView
from formtools.wizard.views import SessionWizardView, NamedUrlSessionWizardView

from core.forms import SharedFuturesWizardView
from remix.forms import (
    StartIdeaLocationStep,
    StartIdeaTitleAndDescriptionStep,
    StartIdeaImagesStep,
    ImageForm,
)
from remix.models import RemixIdea, RemixBackgroundImage
from sfs import settings

REMIX_MODEL_DIR = f"{settings.MEDIA_URL}remix/models"
REMIX_MODEL_PNG_DIR = f"{REMIX_MODEL_DIR}/png"


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


class RemixView(TemplateView):
    template_name = "remix/remix.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        storage = default_storage
        models = []
        if storage.exists("remix/models"):
            _, filenames = storage.listdir("remix/models")
            for filename in sorted(filenames):
                name, ext = splitext(filename)
                if ext == ".glb":
                    models.append(
                        {
                            "name": name,
                            "previewUrl": f"{REMIX_MODEL_PNG_DIR}/{name}.png",
                            "modelUrl": f"{REMIX_MODEL_DIR}/{filename}",
                        }
                    )

        context["models"] = models
        return context
