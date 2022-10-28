from django import forms
from .models import Project
from typing import List

class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields: List[str] = ['name', 'description', 'tags', 'image']
