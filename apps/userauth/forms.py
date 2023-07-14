import os
from typing import Any, Dict, List, Optional, Tuple, Type

from allauth.account.forms import (
    ChangePasswordForm,
    LoginForm,
    ResetPasswordForm,
    ResetPasswordKeyForm,
    SignupForm,
)
from analytics.models import log_signup
from django import forms
from django.http import HttpRequest, QueryDict
from django.utils.translation import gettext_lazy as _
from messaging.models import Message
from wagtail import hooks
from wagtail.users.forms import UserCreationForm, UserEditForm

from .models import CustomUser, Organisation, UserAvatar

"""
Resolving the first&last name issue, reference
Making first and last name optional
https://github.com/brylie/wagtail-social-network/issues/18#issuecomment-892836504
"""


class CustomUserCreationForm(UserCreationForm):
    first_name: forms.CharField = forms.CharField(required=False, label=_("First name"))
    last_name: forms.CharField = forms.CharField(required=False, label=_("Last name"))

    class Meta(UserCreationForm.Meta):
        model: Type[CustomUser] = CustomUser


# these two are used to stop wagtail automatically marking users inactive after editing


@hooks.register("after_edit_user")
def keep_active_status(request, user):
    user.is_active = user.was_active
    user.save()


from django.http import QueryDict
from wagtail import hooks


@hooks.register("before_edit_user")
def check_active_status(request, user):
    user.was_active = user.is_active
    user.save()


class CustomUserEditForm(UserEditForm):
    first_name: forms.CharField = forms.CharField(required=False, label=_("First name"))
    last_name: forms.CharField = forms.CharField(required=False, label=_("Last name"))
    is_active: forms.BooleanField = forms.BooleanField(required=False, initial=True)

    class Meta(UserEditForm.Meta):
        model: Type[CustomUser] = CustomUser
        fields = {
            "post_code",
            "is_active",
            "email",
            "last_name",
            "is_superuser",
            "year_of_birth",
            "display_name",
            "groups",
            "first_name",
        }


class CustomUserNameUpdateForm(forms.ModelForm):
    display_name = forms.CharField(max_length=50)

    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ["display_name"]


class CustomUserAvatarUpdateForm(forms.ModelForm):
    avatar = forms.CharField(max_length=2, required=False)

    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ["avatar"]

    # need to retrieve an instance of the avatar since it's a foreign key to the user
    def clean_avatar(self) -> UserAvatar:
        avatar = self.cleaned_data.get("avatar")
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
        fields: List[str] = ["organisation_name", "organisation_url"]


class CustomUserPostcodeUpdateForm(forms.ModelForm):
    postcode = forms.CharField(max_length=50)

    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ["postcode"]


class CustomSignupForm(SignupForm):
    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ["email", "password1", "password2"]

    def __init__(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.fields["email"].widget.attrs = {
            "placeholder": "Your E-mail",
            "borken": "false",
            "hx-post": "/search/",
            "hx-post": "/profile/check_email/",
            "hx-trigger": "focusout[processEmailValue()] delay:500ms",
            "hx-target": "#email-feedback",
            "hx-swap": "innerHTML",
        }
        self.fields["password1"].widget.attrs = {
            "placeholder": "Password",
            "borken": "false",
            "onfocusout": "getPasswordFeedback()",
        }
        self.fields["password2"].widget.attrs = {
            "placeholder": "Confirm Password",
            "borken": "false",
            "onfocusout": "comparePasswords()",
        }

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
        super(CustomUserAddDataForm, self).__init__(*arg, **kwarg)
        self.empty_permitted = True


class CustomLoginForm(LoginForm):
    error_messages = {
        "email_password_mismatch": "The e-mail address and/or password you provided are not correct, please try again."
    }

    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ["email", "password"]

    def __init__(self, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> None:
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields["login"].widget.attrs = {
            "placeholder": "Your E-mail",
            "borken": "false",
            "onfocusout": "processEmailValue()",
        }
        self.fields["password"].widget.attrs = {
            "placeholder": "Your password",
            "borken": "false",
        }


class CustomChangePasswordForm(ChangePasswordForm):
    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ["oldpassword", "password1", "password2"]

    def __init__(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs = {
            "placeholder": "Password",
            "borken": "false",
            "onfocusout": "getPasswordFeedback()",
        }
        self.fields["password2"].widget.attrs = {
            "placeholder": "Confirm Password",
            "borken": "false",
            "onfocusout": "comparePasswords()",
        }


class CustomResetPasswordForm(ResetPasswordForm):
    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ["email"]

    def __init__(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        super(CustomResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields["email"].widget.attrs = {
            "placeholder": "Your E-mail",
            "borken": "false",
            "onfocusout": "processEmailValue()",
        }


class CustomResetPasswordKeyForm(ResetPasswordKeyForm):
    class Meta:
        model: Type[CustomUser] = CustomUser
        fields: List[str] = ["password1", "password2"]

    def __init__(self, *args: List[Any], **kwargs: Dict[str, Any]) -> None:
        self.user = kwargs.pop("user", None)
        self.temp_key = kwargs.pop("temp_key", None)
        super(ResetPasswordKeyForm, self).__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs = {
            "placeholder": "Password",
            "borken": "false",
            "onfocusout": "getPasswordFeedback()",
        }
        self.fields["password2"].widget.attrs = {
            "placeholder": "Confirm Password",
            "borken": "false",
            "onfocusout": "comparePasswords()",
        }
