import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apiapp.settings')

app = Celery('apiapp')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'check-events-every-30-minutes': {
        'task': 'api.tasks.check_and_complete_events',
        'schedule': crontab(minute='*/45'),  # Every 30 minutes
    },
}