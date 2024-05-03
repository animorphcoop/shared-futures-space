from os.path import basename

from django import forms
from django.core.files import File
from django.core.files.base import ContentFile

from core.forms import LocationField
from core.utils.images import ensure_image_field_crop
from messaging.models import Message
from remix.models import RemixIdea, Remix, RemixBackgroundImage


class StartIdeaLocationStep(forms.ModelForm):
    location = LocationField()

    def __init__(self, *args, current_user=None, **kwargs):
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


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class StartIdeaImagesStep(forms.Form):
    """A form that dynamically adds image fields depending on how many we have"""

    max_count = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_count = min([len(self.files) + 1, self.max_count])
        for i in range(field_count):
            field_name = self.add_prefix(f"image_{i}")
            self.fields[field_name] = forms.ImageField(required=False, label="")


class CreateRemixForm(forms.ModelForm):
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
            remix.scene = source_remix.scene
            remix.background_image = source_remix.background_image

        if commit:
            remix.save()
        return remix

    def copy_background_image_from_message(self, message: Message):
        idea = self.cleaned_data.get("idea")

        background_image = idea.background_images.filter(from_message=message).first()

        if background_image:
            # we can reuse it \o/
            return background_image

        # We have to copy the image
        # This copies it in memory, good enough for now...
        copied_image = ContentFile(message.image.file.read())
        copied_image.name = basename(message.image.name)

        background_image = idea.background_images.create(
            image=copied_image,
            from_message=message,
        )
        ensure_image_field_crop(background_image.image, 16 / 9)

        return background_image

    class Meta:
        model = Remix
        fields = (
            "idea",
            "background_image",
            "message",
        )


class UpdateRemixForm(forms.ModelForm):
    class Meta:
        model = Remix
        fields = (
            "scene",
            "snapshot",
        )
