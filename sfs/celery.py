import os
from celery import Celery

# TODO: Have prod condition to load the other conf
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sfs.settings.dev')

# pyre comment suppresses an error caused by pyre's limited analysis of the celery library
app = Celery('sfs') # pyre-ignore[16]

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
