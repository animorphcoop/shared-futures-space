import os
from typing import Any, Dict, List, Optional, Type

from django import forms
from django.contrib.gis.forms import PointField
from django.contrib.gis.geos import GEOSGeometry
from django.forms import Widget, MultiValueField, RadioSelect

from .models import River
from .widgets import TagsInput, LocationInput, PrecisionRadioSelect


class LocationField(MultiValueField):
    """Custom multi field to set precision and coordinates in one go"""

    def __init__(self):
        super().__init__(
            widget=LocationInput(),
            fields=[
                forms.BooleanField(widget=PrecisionRadioSelect()),
                PointField(),
            ],
            label="Location",
        )

    def compress(self, data_list):
        return data_list


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
    location_with_precision = LocationField()

    def clean(self):
        super().clean()

        # Need to split out the two values
        location_exact, location = self.cleaned_data.pop(
            "location_with_precision",
            (
                True,  # default to exact
                None,
            ),
        )
        self.cleaned_data["location_exact"] = location_exact
        self.cleaned_data["location"] = location

    class Meta:
        model = River
        fields = ["location_with_precision"]


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

    """
    def clean(self):
        print(self)
        print('trying to clean')
        cleaned_data = self.cleaned_data
        image = cleaned_data.get('image')

        if image is not None:
            try:
                extension = os.path.splitext(image.name)[1][1:].lower()
                if extension in self.ALLOWED_IMAGE_TYPES:
                    cleaned_data['image'] = image
                    return cleaned_data
                else:
                    raise forms.ValidationError('Image types is not allowed')
            except Exception as e:
                raise forms.ValidationError('Can not identify file type')

        return cleaned_data
    """
