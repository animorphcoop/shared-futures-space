from typing import List, Type

from core.forms import LocationField
from django import forms
from django.contrib.gis.forms import PointField

from .models import River
from .widgets import TagsInput


class CreateRiverFormStep1(forms.ModelForm):
    class Meta:
        model: Type[River] = River
        fields: List[str] = ["title", "description", "tags", "image"]
        labels = {"image": "Upload an image"}
        widgets = {
            "tags": TagsInput(),
            "description": forms.Textarea(),
        }


class CreateRiverFormStep2(forms.ModelForm):
    location = LocationField(enable_precision=True)

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["location"].widget.current_user = current_user

    def clean(self):
        cleaned_data = super().clean()
        location_fields = cleaned_data.pop("location", None)
        if location_fields:
            cleaned_data["location"] = location_fields["location"]
            cleaned_data["location_exact"] = location_fields["precision"]
        return cleaned_data

    class Meta:
        model = River
        fields = ["location"]


class CreateRiverFormStep3(forms.ModelForm):
    """A step just to show the help file

    The template checks if we're the last step
    and shows the help info if so
    """

    class Meta:
        model = River
        fields = []


class RiverTitleUpdateForm(forms.ModelForm):
    title = forms.CharField(max_length=100)

    class Meta:
        model: Type[River] = River
        fields: List[str] = ["title"]


class RiverDescriptionUpdateForm(forms.ModelForm):
    description = forms.CharField(max_length=100)

    class Meta:
        model: Type[River] = River
        fields: List[str] = ["description"]
        widgets = {
            "description": forms.Textarea(),
        }


class RiverLocationUpdateForm(forms.ModelForm):
    location = PointField(srid=4326)

    class Meta:
        model: Type[River] = River
        fields: List[str] = ["location", "location_exact"]


class RiverImageUpdateForm(forms.ModelForm):
    ALLOWED_IMAGE_TYPES = ["jpg", "jpeg", "png", "webp"]

    class Meta:
        model: Type[River] = River
        fields: List[str] = ["image"]
