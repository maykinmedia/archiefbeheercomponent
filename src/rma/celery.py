from celery import Celery

from rma.setup import setup_env

setup_env()

app = Celery("rma")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
