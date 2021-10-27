from django import forms
from .models import CustomUser

from django.utils.translation import gettext_lazy as _

from wagtail.users.forms import UserEditForm, UserCreationForm

from typing import Type, List

'''
Resolving the first&last name issue, reference
Making first and last name optional
https://github.com/brylie/wagtail-social-network/issues/18#issuecomment-892836504
'''


class CustomUserCreationForm(UserCreationForm):
    first_name: forms.CharField = forms.CharField(required=False, label=_("First name"))
    last_name: forms.CharField = forms.CharField(required=False, label=_("Last name"))

    class Meta(UserCreationForm.Meta):
        model: Type[CustomUser] = CustomUser


class CustomUserEditForm(UserEditForm):
    first_name: forms.CharField = forms.CharField(required=False, label=_("First name"))
    last_name: forms.CharField = forms.CharField(required=False, label=_("Last name"))

    class Meta(UserEditForm.Meta):
        model: Type[CustomUser] = CustomUser


class CustomUserUpdateForm(forms.ModelForm):
    first_name: forms.CharField = forms.CharField(required=False, label=_("First name"))
    last_name: forms.CharField = forms.CharField(required=False, label=_("Last name"))

    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ['display_name', 'year_of_birth', 'post_code']


'''
TODO: Consider adding display_name and age values at the signup?
class SignupForm(forms.Form):
    display_name = forms.CharField(max_length=30, label=_("Display name"),
                                   help_text=_("Will be shown e.g. when commenting."))

    def signup(self, request, user):
        user.display_name = self.cleaned_data['display_name']
        user.save()
'''
