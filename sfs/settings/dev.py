# pyre-strict
from .base import *
from django.conf import settings
from typing import List, Any

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG: bool = True

INSTALLED_APPS += ['debug_toolbar']

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY: str = 'django-insecure-^-*ov6&0l@xp6up7)4sm1i9kgu60nfj#9gg$z+pudx7)2u-+ml'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS: List[str] = ['*']

# just to fix some warnings
DEFAULT_AUTO_FIELD: str = 'django.db.models.BigAutoField'


INTERNAL_IPS: List[str] = [

    '0.0.0.0',

]

# Docker specific, type of values declared as Any because I don't know what the different settings are/can be
DEBUG_TOOLBAR_CONFIG: Dict[str,Any] = {
    #'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG
    "SHOW_TOOLBAR_CALLBACK": lambda x: settings.DEBUG,
}

try:
    from .local import *
except ImportError:
    pass
