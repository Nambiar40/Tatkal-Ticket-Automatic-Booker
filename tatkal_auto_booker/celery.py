import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tatkal_auto_booker.settings")
app = Celery("tatkal_auto_booker")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-and-run-bookings-every-minute': {
        'task': 'booking.tasks.update_scheduled_bookings',
        'schedule': crontab(minute='*'),  # every 1 min
    },
}
