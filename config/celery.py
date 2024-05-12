from celery import Celery
from datetime import timedelta
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
app.conf.beat_schedule = {
    'delete_expired_stories':{
        'task':'accounts.tasks.delete_expired_stories',
        'schedule':timedelta(hours=24),
    }
}