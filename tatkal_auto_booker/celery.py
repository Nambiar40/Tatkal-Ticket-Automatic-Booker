import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tatkal_auto_booker.settings")
app = Celery("tatkal_auto_booker")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()