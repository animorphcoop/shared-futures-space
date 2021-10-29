# pyre-strict
import os
from celery import Celery
from django.conf import settings

if settings.DEBUG:
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sfs.settings.dev')
else:
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sfs.settings.production')

# pyre comment suppresses an error caused by pyre's limited analysis of the celery library
app = Celery('sfs') # pyre-ignore[16]

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
