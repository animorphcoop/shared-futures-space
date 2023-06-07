from typing import Dict
from urllib.parse import parse_qs, urlparse

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse
from userauth.models import CustomUser


# this is to set the personal information of a user who registered through a social account
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(
        self, request: WSGIRequest, sociallogin: SocialLogin, data: Dict[str, str]
    ) -> CustomUser:
        u = sociallogin.user
        if "first_name" in data and "last_name" in data:
            u.display_name = data["first_name"] + " " + data["last_name"]
        else:
            u.display_name = "New User"
        if "email" in data:
            u.email = data["email"]
        return u

    def get_login_redirect_url(self, request: WSGIRequest) -> str:
        if "HTTP_REFERER" in request.META:
            qs = parse_qs(urlparse(request.META["HTTP_REFERER"]).query)
        else:
            qs = {}
        if "next" in qs:
            return qs["next"][0]
        else:
            return reverse("dashboard")
