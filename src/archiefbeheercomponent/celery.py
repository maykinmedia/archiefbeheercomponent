from celery import Celery

from archiefbeheercomponent.setup import setup_env

setup_env()

app = Celery("archiefbeheercomponent")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
