from django import forms
from .models import CustomUser

from wagtail.users.forms import UserEditForm, UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser


class CustomUserEditForm(UserEditForm):
    class Meta(UserEditForm.Meta):
        model = CustomUser
