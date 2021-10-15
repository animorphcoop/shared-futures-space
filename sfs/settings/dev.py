from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^-*ov6&0l@xp6up7)4sm1i9kgu60nfj#9gg$z+pudx7)2u-+ml'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

# just to fix some warnings
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ALLAUTH:

SITE_ID = 1

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

INSTALLED_APPS = INSTALLED_APPS + [
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount']

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

try:
    from .local import *
except ImportError:
    pass
