# pyre-strict

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.core.handlers.wsgi import WSGIRequest
from userauth.models import CustomUser # pyre-ignore[21]
from typing import Dict

# this is to set the personal information of a user who registered through a social account
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request: WSGIRequest, sociallogin: SocialLogin, data: Dict[str,str]) -> CustomUser: # pyre-ignore[11]
        u = sociallogin.user
        if 'first_name' in data and 'last_name' in data:
            u.display_name = data['first_name'] + " " + data['last_name']
        else:
            u.display_name = 'New User'
        if 'email' in data:
            u.email = data['email']
        return u
