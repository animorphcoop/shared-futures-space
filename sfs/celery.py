import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sfs.settings.settings')

app = Celery('sfs')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks() # currently just the one - apps/userauth/tasks.py:send_after (but don't trust this comment to be up to date)
