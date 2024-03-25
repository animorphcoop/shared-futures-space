import os
from typing import List, Type

from django import forms

from .models import Message


class ChatForm(forms.ModelForm):
    ALLOWED_IMAGE_TYPES = ["jpg", "jpeg", "png", "gif", "webp"]
    ALLOWED_DOC_TYPES = [
        "pdf",
        "odt",
        "docx",
        "doc",
        "rtf",
        "txt",
        "md",
        "ods",
        "xlsx",
        "csv",
    ]

    class Meta:
        model: Type[Message] = Message
        fields: List[str] = ["text", "image", "file"]

    def clean(self):
        cleaned_data = self.cleaned_data
        file = cleaned_data.get("file")

        if file is not None:
            try:
                extension = os.path.splitext(file.name)[1][1:].lower()
                if extension in self.ALLOWED_DOC_TYPES:
                    return cleaned_data
                elif extension in self.ALLOWED_IMAGE_TYPES:
                    cleaned_data["image"] = cleaned_data["file"]
                    cleaned_data["file"] = None
                    return cleaned_data
                else:
                    raise forms.ValidationError("File types is not allowed")
            except Exception:
                raise forms.ValidationError("Can not identify file type")

        return cleaned_data
