from django.core.management.base import BaseCommand
from django.db import transaction

from timeline_logger.models import TimelineLog


class Command(BaseCommand):
    help = "Change the extension of the log templates from .txt to .html"

    def handle(self, *args, **options):
        logs = TimelineLog.objects.all()

        with transaction.atomic():
            for log in logs:
                template_name = log.template
                if ".txt" in template_name:
                    log.template = template_name.replace(".txt", ".html")
                    log.save()
