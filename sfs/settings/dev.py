from .base import *
from django.conf import settings

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS += ['debug_toolbar']

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^-*ov6&0l@xp6up7)4sm1i9kgu60nfj#9gg$z+pudx7)2u-+ml'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

# just to fix some warnings
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


INTERNAL_IPS = [

    '0.0.0.0',

]

# Docker specific
DEBUG_TOOLBAR_CONFIG = {
    #'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG
    "SHOW_TOOLBAR_CALLBACK": lambda x: settings.DEBUG,
}

try:
    from .local import *
except ImportError:
    pass
