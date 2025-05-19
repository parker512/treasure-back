# back/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')

app = Celery('back')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# back/celery.py
from celery.schedules import crontab

app.conf.beat_schedule = {
    'auto-complete-transactions-every-hour': {
        'task': 'books.tasks.auto_complete_transactions',
        'schedule': crontab(minute=0, hour='*'),  # Run every hour
    },
}