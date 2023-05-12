from django import forms
from .models import River
from typing import Type, List, Any, Dict, Optional


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

