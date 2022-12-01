from django import forms

from django.core.exceptions import ValidationError
from .models import Message
from typing import Type, List

import os

class ChatForm(forms.ModelForm):
    ALLOWED_IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    ALLOWED_DOC_TYPES = ['pdf', 'odt', 'docx', 'doc', 'rtf', 'txt', 'md', 'ods', 'xlsx', 'csv']

    class Meta:
        model: Type[Message] = Message  # pyre-ignore[11]
        fields: List[str] = ['text', 'image', 'file']


    def clean(self):
        cleaned_data = self.cleaned_data
        file = cleaned_data.get('file')
        print(file)

        if file is not None:
            print('in')
            try:
                extension = os.path.splitext(file.name)[1][1:].lower()
                if extension in self.ALLOWED_DOC_TYPES:
                    return cleaned_data
                elif extension in self.ALLOWED_IMAGE_TYPES:
                    cleaned_data['image'] = cleaned_data['file']
                    cleaned_data['file'] = None
                    return cleaned_data
                else:
                    raise forms.ValidationError('File types is not allowed')
            except Exception as e:
                raise forms.ValidationError('Can not identify file type')

        return cleaned_data
