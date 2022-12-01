# pyre-strict
from django import forms
from .models import CustomUser, Organisation, UserAvatar
from analytics.models import log_signup  # pyre-ignore[21]
from messaging.models import Message  # pyre-ignore[21]

from django.utils.translation import gettext_lazy as _

from allauth.account.forms import SignupForm, LoginForm, ResetPasswordForm, ChangePasswordForm, ResetPasswordKeyForm
from wagtail.users.forms import UserEditForm, UserCreationForm

from typing import Type, List, Any, Dict, Tuple, Optional
from django.http import HttpRequest

import os

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


class CustomUserNameUpdateForm(forms.ModelForm):
    display_name = forms.CharField(max_length=50)

    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ['display_name']


class CustomUserAvatarUpdateForm(forms.ModelForm):
    avatar = forms.CharField(max_length=2, required=False)

    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ['avatar']

    # need to retrieve an instance of the avatar since it's a foreign key to the user
    def clean_avatar(self) -> UserAvatar:
        avatar = self.cleaned_data.get('avatar')
        try:
            avatar_instance = UserAvatar.objects.get(pk=avatar)
        except UserAvatar.DoesNotExist:
            avatar_instance = None
        return avatar_instance


class CustomUserOrganisationUpdateForm(forms.ModelForm):
    organisation_name = forms.CharField(max_length=50)
    organisation_url = forms.CharField(max_length=100, required=False)

    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ['organisation_name', 'organisation_url']


class CustomSignupForm(SignupForm):
    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ['email', 'password1', 'password2']

    def __init__(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs = {'placeholder': 'Your E-mail', 'borken': 'false', 'hx-post': '/search/',
                                             'hx-post': '/profile/check_email/',
                                             'hx-trigger': 'focusout[processEmailValue()] delay:500ms',
                                             'hx-target': '#email-feedback', 'hx-swap': 'innerHTML'}
        self.fields['password1'].widget.attrs = {'placeholder': 'Password', 'borken': 'false',
                                                 'onfocusout': 'getPasswordFeedback()'}
        self.fields['password2'].widget.attrs = {'placeholder': 'Confirm Password', 'borken': 'false',
                                                 'onfocusout': 'comparePasswords()'}

    def save(self, request: HttpRequest) -> CustomUser:
        user = super(CustomSignupForm, self).save(request)
        user.save()
        log_signup(user)  # analytics
        return user


class CustomUserAddDataForm(forms.Form):
    display_name = forms.CharField(max_length=50)
    year_of_birth = forms.IntegerField()
    post_code = forms.CharField(max_length=8)
    avatar = forms.CharField(max_length=2, required=False)
    organisation_name = forms.CharField(max_length=50, required=False)
    organisation_url = forms.CharField(max_length=100, required=False)

    def __init__(self, *arg: List[Any], **kwarg: Dict[str, Any]) -> None:
        super(CustomUserAddDataForm, self).__init__(*arg, **kwarg)  # pyre-ignore[6]
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
        self.fields['login'].widget.attrs = {'placeholder': 'Your E-mail', 'borken': 'false',
                                             'onfocusout': 'processEmailValue()'}
        self.fields['password'].widget.attrs = {'placeholder': 'Your password', 'borken': 'false', }


class CustomChangePasswordForm(ChangePasswordForm):
    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ['oldpassword', 'password1', 'password2']

    def __init__(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs = {'placeholder': 'Password', 'borken': 'false',
                                                 'onfocusout': 'getPasswordFeedback()'}
        self.fields['password2'].widget.attrs = {'placeholder': 'Confirm Password', 'borken': 'false',
                                                 'onfocusout': 'comparePasswords()'}


class CustomResetPasswordForm(ResetPasswordForm):
    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ['email']

    def __init__(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        super(CustomResetPasswordForm, self).__init__(*args, **kwargs)  # pyre-ignore[6]
        self.fields['email'].widget.attrs = {'placeholder': 'Your E-mail', 'borken': 'false',
                                             'onfocusout': 'processEmailValue()'}


class CustomResetPasswordKeyForm(ResetPasswordKeyForm):
    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ['password1', 'password2']

    def __init__(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        self.user = kwargs.pop("user", None)  # pyre-ignore[4]
        self.temp_key = kwargs.pop("temp_key", None)  # pyre-ignore[4]
        super(ResetPasswordKeyForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs = {'placeholder': 'Password', 'borken': 'false',
                                                 'onfocusout': 'getPasswordFeedback()'}
        self.fields['password2'].widget.attrs = {'placeholder': 'Confirm Password', 'borken': 'false',
                                                 'onfocusout': 'comparePasswords()'}

