# pyre-strict
from django import forms
from .models import CustomUser
from analytics.models import log_signup # pyre-ignore[21]

from django.utils.translation import gettext_lazy as _

from allauth.account.forms import SignupForm, LoginForm
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
    class Meta(UserEditForm.Meta):
        model: Type[CustomUser] = CustomUser


class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ['display_name', 'email', 'avatar']


class CustomSignupForm(SignupForm):
    display_name = forms.CharField(max_length=30, label=_("Display name"),
                                   help_text=_("Will be shown e.g. when commenting."))
    organisation = forms.BooleanField(required=False, label="organisation")

    def save(self, request: HttpRequest) -> CustomUser:
        user = super(CustomSignupForm, self).save(request)
        user.display_name = self.cleaned_data['display_name'] # pyre-ignore[16]
        user.organisation = self.cleaned_data['organisation']
        user.save()
        log_signup(user, request) # analytics
        return user


'''
class CustomUserLoginForm(LoginForm):
    class Meta(LoginForm.Meta):
        model: Type[CustomUser] = CustomUser
'''

class CustomUserPersonalForm(forms.Form):
    year_of_birth = forms.IntegerField()
    post_code = forms.CharField(max_length = 8)

class CustomLoginForm(LoginForm):

    error_messages = {
        "email_password_mismatch": "Your password does not match, try again."
    }

#class CustomLoginForm(LoginForm):
