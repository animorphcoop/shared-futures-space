# pyre-strict
"""
WSGI config for sfs project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.conf import settings


from django.core.wsgi import get_wsgi_application
from django.core.handlers.wsgi import WSGIHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sfs.settings.settings")

application: WSGIHandler = get_wsgi_application()
