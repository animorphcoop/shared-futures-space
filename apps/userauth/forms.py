# pyre-strict
from django import forms
from .models import CustomUser, Organisation
from analytics.models import log_signup  # pyre-ignore[21]

from django.utils.translation import gettext_lazy as _

from allauth.account.forms import SignupForm, LoginForm, ResetPasswordForm
from wagtail.users.forms import UserEditForm, UserCreationForm

from typing import Type, List, Any, Dict
from django.http import HttpRequest
from typing import Tuple

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
    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ['email', 'password1', 'password2']

    def __init__(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs = {'borken': 'false', 'hx-post': '/search/',
                                             'hx-post': '/account/check_email/',
                                             'hx-trigger': 'focusout[processEmailValue()] delay:500ms',
                                             'hx-target': '#email-feedback', 'hx-swap': 'innerHTML'}
        self.fields['password1'].widget.attrs = {'borken': 'false', 'onfocusout': 'getPasswordFeedback()'}
        self.fields['password2'].widget.attrs = {'borken': 'false', 'onfocusout': 'comparePasswords()'}

    def save(self, request: HttpRequest) -> CustomUser:
        user = super(CustomSignupForm, self).save(request)
        user.save()
        log_signup(user, request)  # analytics
        return user


class CustomUserPersonalForm(forms.Form):
    display_name = forms.CharField(max_length=50)
    year_of_birth = forms.IntegerField()
    post_code = forms.CharField(max_length=8)
    avatar = forms.CharField(max_length=2, required=False)
    organisation_name = forms.CharField(max_length=50, required=False)
    organisation_url = forms.CharField(max_length=100, required=False)

    def __init__(self, *arg: List[Any], **kwarg: Dict[str, Any]) -> None:
        super(CustomUserPersonalForm, self).__init__(*arg, **kwarg)  # pyre-ignore[6]
        self.empty_permitted = True


class CustomLoginForm(LoginForm):
    error_messages = {
        "email_password_mismatch": "The e-mail address and/or password you provided are not correct, please try again."

    }

    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ['email', 'password']

    def __init__(self, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> None:
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget.attrs = {'borken': 'false', 'onfocusout': 'processEmailValue()'}
        self.fields['password'].widget.attrs = {'borken': 'false', }


class CustomResetPasswordForm(ResetPasswordForm):
    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ['email']

    def __init__(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        super(CustomResetPasswordForm, self).__init__(*args, **kwargs)  # pyre-ignore[6]
        self.fields['email'].widget.attrs = {'borken': 'false', 'onfocusout': 'processEmailValue()'}
