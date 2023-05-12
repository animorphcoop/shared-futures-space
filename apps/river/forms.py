from django import forms
from .models import River
from typing import Type, List, Any, Dict, Optional

import os


class CreateRiverForm(forms.ModelForm):
    class Meta:
        model: Type[River] = River
        fields: List[str] = ['title', 'description', 'tags', 'image']
        widgets = {
            'description': forms.Textarea(),
        }


class RiverTitleUpdateForm(forms.ModelForm):
    title = forms.CharField(max_length=100)

    class Meta:
        model: Type[River] = River
        fields: List[str] = ['title']


class RiverDescriptionUpdateForm(forms.ModelForm):
    description = forms.CharField(max_length=100)

    class Meta:
        model: Type[River] = River
        fields: List[str] = ['description']
        widgets = {
            'description': forms.Textarea(),
        }

class RiverImageUpdateForm(forms.ModelForm):
    ALLOWED_IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'webp']

    class Meta:
        model: Type[River] = River
        fields: List[str] = ['image']

    def clean(self):
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

