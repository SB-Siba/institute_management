from __future__ import absolute_import, unicode_literals
from celery import Celery
import os
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'niwa_agro.settings')

app = Celery('niwa_agro')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'delete-expired-accounts-every-day': {
        'task': 'users.tasks.delete_expired_accounts',
        'schedule': crontab(hour=0, minute=0),  # Runs daily at midnight
    },
}