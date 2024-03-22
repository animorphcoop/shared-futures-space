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

    def clean(self):
        cleaned_data = super().clean()
        location_fields = cleaned_data.pop("location")
        cleaned_data["location"] = location_fields["location"]
        cleaned_data["location_exact"] = location_fields["precision"]
        return cleaned_data

    class Meta:
        model = River
        fields = ["location"]


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
