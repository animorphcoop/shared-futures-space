from django import forms

from core.forms import LocationField
from remix.models import RemixIdea, Remix


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
    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        remix = super().save(commit=False)
        remix.user = self.request.user
        if commit:
            remix.save()
        return remix

    class Meta:
        model = Remix
        fields = (
            "idea",
            "background_image",
        )


class UpdateRemixForm(forms.ModelForm):
    class Meta:
        model = Remix
        fields = (
            "scene",
            "snapshot",
        )
