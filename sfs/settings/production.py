# pyre-strict

from .base import *
from django.conf import settings
from typing import List, Any
from django.core.handlers.wsgi import WSGIRequest

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG: bool = False

# SECURITY WARNING: keep the secret key used in production secret!
# commented out so it has to be newly set in production
# SECRET_KEY: str = ''

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS: List[str] = ['sharedfutures.space']

# just to fix some warnings, becomes relevant in next django version apparently
DEFAULT_AUTO_FIELD: str = 'django.db.models.BigAutoField'

INTERNAL_IPS: List[str] = [

    '0.0.0.0',

]

try:
    from .local import *
except ImportError:
    pass
