# pyre-strict
from typing import List, Optional
from .base import INSTALLED_APPS

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY: str = '_J(I)NBO*OYNO(M0[mun89pyP (8h8 9)M*MJ<"{KKT FUTYg iuytyp9||\ReU'

SITE_ID = 1
SITE_DOMAIN = 'sharedfutures.space'

INSTALLED_APPS += [
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google'
]

AUTHENTICATION_BACKENDS: List[str] = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# !!!!! SECURITY WARNING !!!!!
# these are our actual creds, they MUST be changed on the relevant accounts before publishing the repo
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'APP': {
            'client_id': '859293604779855',
            'secret': '1bfdb6d39f61f7ced097634b84610b26',
            'key': ''
        }
    },
    'google': {
        'APP': {
            'client_id': '961383502349-qjmt77m2n1pm9s8fqr3rp2fgcdoot3qc.apps.googleusercontent.com',
            'secret': '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',
            'key': ''
        }
    }
}

LOGIN_REDIRECT_URL: str = '/dashboard/'
LOGOUT_REDIRECT_URL: str = '/'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL: Optional[str] = LOGIN_REDIRECT_URL
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL: Optional[str] = None

ACCOUNT_AUTHENTICATION_METHOD: str = 'email'
ACCOUNT_EMAIL_REQUIRED: bool = True
ACCOUNT_EMAIL_VERIFICATION: str = 'mandatory'
ACCOUNT_USERNAME_REQUIRED: bool = False

# !!!!! SECURITY WARNING !!!!!
# these are our actual creds, they MUST be changed on the relevant accounts before publishing the repo
EMAIL_HOST: str = 'mail.webarch.net'
EMAIL_PORT: int = 465
EMAIL_HOST_USER: str = 'sfs_mailer@animorph.coop'
EMAIL_HOST_PASSWORD: str = '7{zjA+b!xWLe5i>C[)U6jOx<gQe(x9g'
EMAIL_USE_TLS: bool = False
EMAIL_USE_SSL: bool = True
DEFAULT_FROM_EMAIL: str = EMAIL_HOST_USER

ACCOUNT_DEFAULT_HTTP_PROTOCOL='https'

# custom user model
AUTH_USER_MODEL: str = 'userauth.CustomUser'

#overriding default account
ACCOUNT_ADAPTER: str = 'userauth.views.CustomAllauthAdapter'
SOCIALACCOUNT_ADAPTER = 'userauth.adapters.CustomSocialAccountAdapter'

# pickle required to serialize and send EmailMultiAlternatives
# https://docs.celeryproject.org/en/latest/userguide/calling.html#calling-serializers
CELERY_ACCEPT_CONTENT: List[str] = ['pickle']
CELERY_TASK_SERIALIZER: str = 'pickle'
CELERY_RESULT_SERIALIZER: str = 'pickle'
