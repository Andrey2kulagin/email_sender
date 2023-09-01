import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'cool_sender.settings')
app = Celery('cool_sender')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
