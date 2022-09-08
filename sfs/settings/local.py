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
            'client_id': '780510723095271',
            'secret': '28cd8f0f9c8bfaae6dd4a732c56fa8e6',
            'key': ''
        },
        'logo': '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><g clip-path="url(#clip0_2270_9315)"><path d="M16 8C16 3.58172 12.4183 0 8 0C3.58172 0 0 3.58172 0 8C0 11.993 2.92547 15.3027 6.75 15.9028V10.3125H4.71875V8H6.75V6.2375C6.75 4.2325 7.94438 3.125 9.77172 3.125C10.6467 3.125 11.5625 3.28125 11.5625 3.28125V5.25H10.5538C9.56 5.25 9.25 5.86672 9.25 6.5V8H11.4688L11.1141 10.3125H9.25V15.9028C13.0745 15.3027 16 11.993 16 8Z" fill="#1877F2"/><path d="M11.1141 10.3125L11.4688 8H9.25V6.5C9.25 5.86734 9.56 5.25 10.5538 5.25H11.5625V3.28125C11.5625 3.28125 10.647 3.125 9.77172 3.125C7.94438 3.125 6.75 4.2325 6.75 6.2375V8H4.71875V10.3125H6.75V15.9028C7.5783 16.0324 8.4217 16.0324 9.25 15.9028V10.3125H11.1141Z" fill="white"/></g><defs><clipPath id="clip0_2270_9315"><rect width="16" height="16" fill="white"/></clipPath></defs></svg>'
    },
    'google': {
        'APP': {
            'client_id': '952892024794-dr53p12mssmv41j362o46h92nktmh5b6.apps.googleusercontent.com',
            'secret': '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',
            'key': ''
        },
        'logo': '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><g clip-path="url(#clip0_2270_9308)"><path d="M15.8439 8.18417C15.8439 7.64035 15.7998 7.09359 15.7058 6.55859H8.15991V9.63925H12.4811C12.3018 10.6328 11.7256 11.5117 10.8819 12.0703V14.0692H13.4599C14.9738 12.6758 15.8439 10.6181 15.8439 8.18417Z" fill="#4285F4"/><path d="M8.15999 16.0007C10.3176 16.0007 12.1372 15.2923 13.4629 14.0694L10.885 12.0705C10.1677 12.5585 9.24174 12.8348 8.16293 12.8348C6.07584 12.8348 4.30623 11.4268 3.67128 9.53369H1.01099V11.5943C2.36906 14.2958 5.13518 16.0007 8.15999 16.0007V16.0007Z" fill="#34A853"/><path d="M3.66827 9.53331C3.33316 8.53974 3.33316 7.46386 3.66827 6.4703V4.40967H1.01091C-0.123755 6.67018 -0.123755 9.33342 1.01091 11.5939L3.66827 9.53331V9.53331Z" fill="#FBBC04"/><path d="M8.15999 3.16644C9.30053 3.1488 10.4029 3.57798 11.2289 4.36578L13.5129 2.08174C12.0667 0.72367 10.1471 -0.0229773 8.15999 0.000539111C5.13518 0.000539111 2.36906 1.70548 1.01099 4.40987L3.66834 6.4705C4.30035 4.57449 6.0729 3.16644 8.15999 3.16644V3.16644Z" fill="#EA4335"/></g><defs><clipPath id="clip0_2270_9308"><rect width="16" height="16" fill="white"/></clipPath></defs></svg>'
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
