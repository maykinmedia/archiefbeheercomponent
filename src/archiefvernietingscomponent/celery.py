from celery import Celery

from archiefvernietingscomponent.setup import setup_env

setup_env()

app = Celery("archiefvernietingscomponent")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
