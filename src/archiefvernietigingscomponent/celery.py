from celery import Celery

from archiefvernietigingscomponent.setup import setup_env

setup_env()

app = Celery("archiefvernietigingscomponent")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
