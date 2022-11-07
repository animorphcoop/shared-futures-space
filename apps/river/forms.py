from django import forms
from .models import River
from typing import Type, List, Any, Dict, Optional
from messaging.models import Message # pyre-ignore[21]


class CreateRiverForm(forms.ModelForm):
    class Meta:
        model = River
        fields: List[str] = ['title', 'description', 'tags', 'image']
        widgets = {
            'description': forms.Textarea(),
        }


class RiverChatForm(forms.ModelForm):
    class Meta:
        model: Type[Message] = Message  # pyre-ignore[11]
        fields: List[str] = ['text', 'image', 'file']
    def __init__(self, *args: Optional[Any], **kwargs: Dict[str, Any]) -> None:
        super(RiverChatForm, self).__init__(*args, **kwargs)
