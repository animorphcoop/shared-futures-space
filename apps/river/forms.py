from django import forms
from .models import River
from typing import List

class CreateRiverForm(forms.ModelForm):
    class Meta:
        model = River
        fields: List[str] = ['name', 'description', 'tags', 'image']
