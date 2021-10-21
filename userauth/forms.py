from django import forms
from .models import CustomUser

from django.utils.translation import gettext_lazy as _

from wagtail.users.forms import UserEditForm, UserCreationForm



'''
Resolving the first&last name issue, reference
Making first and last name optional
https://github.com/brylie/wagtail-social-network/issues/18#issuecomment-892836504
'''

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=False, label=_("First name"))
    last_name = forms.CharField(required=False, label=_("Last name"))

    class Meta(UserCreationForm.Meta):
        model = CustomUser


class CustomUserEditForm(UserEditForm):
    first_name = forms.CharField(required=False, label=_("First name"))
    last_name = forms.CharField(required=False, label=_("Last name"))

    class Meta(UserEditForm.Meta):
        model = CustomUser


class CustomUserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(required=False, label=_("First name"))
    last_name = forms.CharField(required=False, label=_("Last name"))

    class Meta:
        model = CustomUser

        fields = ['display_name', 'year_of_birth', 'post_code']
