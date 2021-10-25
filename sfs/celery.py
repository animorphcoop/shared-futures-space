import os
from celery import Celery

# TODO: Have prod condition to load the other conf
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sfs.settings.dev')

app = Celery('sfs')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
