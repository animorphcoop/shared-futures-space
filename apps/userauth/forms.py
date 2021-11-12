# pyre-strict
from django import forms
from .models import CustomUser

from django.utils.translation import gettext_lazy as _

from allauth.account.forms import SignupForm

from wagtail.users.forms import UserEditForm, UserCreationForm

from typing import Type, List, Any
from django.http import HttpRequest

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
    # commented because might actually turn out to break something, same below
    #first_name: forms.CharField = forms.CharField(required=False, label=_("First name"))
    #last_name: forms.CharField = forms.CharField(required=False, label=_("Last name"))

    class Meta(UserEditForm.Meta):
        model: Type[CustomUser] = CustomUser


class CustomUserUpdateForm(forms.ModelForm):
    #first_name: forms.CharField = forms.CharField(required=False, label=_("First name"))
    #last_name: forms.CharField = forms.CharField(required=False, label=_("Last name"))

    class Meta:
        model: Type[CustomUser] = CustomUser
        #fields: List[str] = ['display_name', 'year_of_birth', 'post_code']
        fields: List[str] = ['display_name', 'email', 'avatar']

class CustomSignupForm(SignupForm):
    display_name = forms.CharField(max_length=30, label=_("Display name"),
                                   help_text=_("Will be shown e.g. when commenting."))
    def save(self, request: HttpRequest) -> CustomUser:
        user = super(CustomSignupForm, self).save(request)
        user.display_name = self.cleaned_data['display_name'] # pyre-ignore[16] - it clearly does have this attrbute, since it works
        user.save()
        return user
