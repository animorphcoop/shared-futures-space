from django import forms

from django.core.exceptions import ValidationError
from .models import Message
from typing import Type, List

import os

class ChatForm2(forms.ModelForm):
    ALLOWED_IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif']
    ALLOWED_DOC_TYPES = ['pdf', 'odt', 'docx', 'gif', 'ods', 'xlsx']

    class Meta:
        model: Type[Message] = Message  # pyre-ignore[11]
        fields: List[str] = ['text', 'image', 'file']

    '''
    def is_valid(self):
        # run whatever ModelForm validations you need
        print('is this here?')
        return super(ChatForm2, self).is_valid()
    '''

    def clean_file(self):
        #cleaned_data = super(ChatForm2, self).clean()
        print('wetf')
        file = self.cleaned_data.get('file', None)
        print(file)
        #return self.cleaned_data['file']
        #file = cleaned_data.get('file', None)

        # cleaned_data = super(ChatForm, self).clean()
        # file = cleaned_data.get('file', None)
        #print(file)
        return file

        '''
        try:
            extension = os.path.splitext(file.name)[1][1:].lower()
            if extension in self.ALLOWED_IMAGE_TYPES:
                print('its an image')
                return file
            elif extension in self.ALLOWED_DOC_TYPES:
                print('its an file')
                return file
            else:
                raise forms.ValidationError('File types is not allowed')
        except Exception as e:
            raise forms.ValidationError('Can not identify file type')
        '''

