from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todo_site.settings')

app = Celery('todo_site')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'send_task_notifications_daily': {
        'task': 'todo.tasks.send_task_notifications',
        'schedule': crontab(hour=18, minute=40),  # Runs every day at the given time
    },
}
