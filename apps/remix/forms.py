from os.path import basename

from django import forms
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.base import ContentFile
from django.forms import ModelChoiceField

from core.forms import LocationField
from core.utils.images import ensure_image_field_crop, copy_image_field
from messaging.models import Message
from remix.models import RemixIdea, Remix, RemixBackgroundImage


class HelpStep(forms.Form):
    """Just a step to show the help info"""

    pass


class StartIdeaLocationStep(forms.ModelForm):
    location = LocationField(marker_type="idea")

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop("current_user", None)
        super().__init__(*args, **kwargs)
        self.fields["location"].widget.current_user = current_user

    def clean(self):
        cleaned_data = super().clean()
        location_fields = cleaned_data.pop("location", None)
        if location_fields:
            cleaned_data["location"] = location_fields["location"]
        return cleaned_data

    class Meta:
        model = RemixIdea
        fields = ("location",)


class StartIdeaTitleAndDescriptionStep(forms.ModelForm):
    class Meta:
        model = RemixIdea
        fields = ("title", "description")


class StartIdeaImagesStep(forms.Form):
    """A form that dynamically adds image fields depending on how many we have"""

    max_count = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_count = min([len(self.files) + 1, self.max_count])
        for i in range(field_count):
            field_name = f"image_{i}"
            self.fields[field_name] = forms.ImageField(required=False, label="")

    def clean(self):
        cleaned_data = super().clean()
        # TODO: validate there is at least one image
        # For some reason when it's called on the final submit it gets
        # called with no images or files :/ Not sure why...
        # if len([image for image in cleaned_data.values() if image]) == 0:
        #     raise ValidationError("Must provide at least one image")
        return cleaned_data


class CreateRemixForm(forms.ModelForm):
    # override this to set required=False
    idea = ModelChoiceField(queryset=RemixIdea.objects, required=False)

    # Sources of remix background images are:

    # 1. an idea initial background image
    background_image = forms.ModelChoiceField(
        queryset=RemixBackgroundImage.objects.filter(initial_image=True), required=False
    )

    # 2. a chat message image
    message = forms.ModelChoiceField(queryset=Message.objects, required=False)

    # 3. another remix
    remix = forms.ModelChoiceField(queryset=Remix.objects, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        # TODO: check the background_image/remix/message are from this idea
        # or raise a ValidationError
        return cleaned_data

    def save(self, commit=True):
        remix = super().save(commit=False)
        remix.user = self.request.user

        if message := self.cleaned_data.get("message", None):
            remix.background_image = self.copy_background_image_from_message(message)
        if source_remix := self.cleaned_data.get("remix", None):
            remix.from_remix = source_remix
            remix.scene = source_remix.scene
            remix.background_image = source_remix.background_image
            if not remix.idea_id:
                remix.idea = source_remix.idea

        if commit:
            remix.save()
        return remix

    def copy_background_image_from_message(self, message: Message):
        idea = self.cleaned_data.get("idea")

        background_image = idea.background_images.filter(from_message=message).first()

        if background_image:
            # we can reuse it \o/
            return background_image

        background_image = idea.background_images.create(
            image=copy_image_field(message.image),
            from_message=message,
        )
        # messages images might not be the right aspect ratio
        ensure_image_field_crop(background_image.image, 16 / 9)

        return background_image

    class Meta:
        model = Remix
        fields = (
            "idea",
            "background_image",
            "message",
            "remix",
        )


class UpdateRemixForm(forms.ModelForm):
    class Meta:
        model = Remix
        fields = (
            "scene",
            "snapshot",
        )
