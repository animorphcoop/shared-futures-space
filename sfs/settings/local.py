from os.path import exists
from typing import Dict, List, Optional

from .base import INSTALLED_APPS

if exists("sfs/settings/secrets.py"):
    from .secrets import (
        EMAIL_HOST_PASSWORD,
        FACEBOOK_CLIENT_ID,
        FACEBOOK_SECRET,
        GOOGLE_CLIENT_ID,
        GOOGLE_SECRET,
        SECRET_KEY,
        WEATHER_API_KEY,
    )
else:
    # dummy values to avoid crashing anything entirely
    SECRET_KEY = "..."
    WEATHER_API_KEY = "..."
    EMAIL_HOST_PASSWORD = "..."
    FACEBOOK_CLIENT_ID = "..."
    FACEBOOK_SECRET = "..."
    GOOGLE_CLIENT_ID = "..."
    GOOGLE_SECRET = "..."

SECRET_KEY = SECRET_KEY

SITE_ID = 1
SITE_DOMAIN = "sharedfutures.space"

INSTALLED_APPS += [
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.google",
]

AUTHENTICATION_BACKENDS: List[str] = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SOCIALACCOUNT_PROVIDERS: Dict[str, Dict[str, Dict[str, str]]] = {
    "facebook": {
        "APP": {"client_id": FACEBOOK_CLIENT_ID, "secret": FACEBOOK_SECRET, "key": ""}
    },
    "google": {
        "APP": {"client_id": GOOGLE_CLIENT_ID, "secret": GOOGLE_SECRET, "key": ""}
    },
}

LOGOUT_REDIRECT_URL: str = "/"
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL: Optional[str] = "/dashboard/"
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL: Optional[str] = None

ACCOUNT_AUTHENTICATION_METHOD: str = "email"
ACCOUNT_EMAIL_REQUIRED: bool = True
ACCOUNT_EMAIL_VERIFICATION: str = "mandatory"
ACCOUNT_USERNAME_REQUIRED: bool = False

EMAIL_HOST: str = "mail.webarch.net"
EMAIL_PORT: int = 465
EMAIL_HOST_USER: str = "sfs_mailer@animorph.coop"
EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD
EMAIL_USE_TLS: bool = False
EMAIL_USE_SSL: bool = True
DEFAULT_FROM_EMAIL: str = EMAIL_HOST_USER

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

# custom user model
AUTH_USER_MODEL: str = "userauth.CustomUser"

# overriding default account
ADAPTER: str = "userauth.views.CustomAllauthAdapter"
ACCOUNT_ADAPTER: str = "userauth.views.CustomAllauthAdapter"
SOCIALACCOUNT_ADAPTER = "userauth.adapters.CustomSocialAccountAdapter"

# pickle required to serialize and send EmailMultiAlternatives
# https://docs.celeryproject.org/en/latest/userguide/calling.html#calling-serializers
CELERY_ACCEPT_CONTENT: List[str] = ["pickle"]
CELERY_TASK_SERIALIZER: str = "pickle"
CELERY_RESULT_SERIALIZER: str = "pickle"

WEATHER_API_KEY = WEATHER_API_KEY
