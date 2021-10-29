# pyre-strict

from .base import *
from django.conf import settings
from typing import List, Any
from django.core.handlers.wsgi import WSGIRequest

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG: bool = False


# SECRET_KEY: str = 'Q%Ohhtu$DbbtCvJMaspG31Ijsx0piYLAI4gUNpyxzpRVuxaUlbn(XKW'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS: List[str] = ['dev.sharedfutures.space', 'sharedfutures.space']

# just to fix some warnings, becomes relevant in next django version apparently
DEFAULT_AUTO_FIELD: str = 'django.db.models.BigAutoField'


try:
    from .local import *
except ImportError:
    pass