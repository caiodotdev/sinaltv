import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinaltv.settings')

app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'channels-collect': {
        'task': 'app.tasks.fetch_channels',
        'schedule': crontab(minute="*/5"),
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
