from django.apps import AppConfig, apps
from django.conf import settings
from django.contrib.contenttypes.management import create_contenttypes
from django.core.management import call_command
from django.db.models.signals import post_migrate


def update_admin_index(sender, **kwargs):
    from django_admin_index.models import AppGroup

    AppGroup.objects.all().delete()

    for app in settings.INSTALLED_APPS:
        if app.startswith("archiefbeheercomponent"):
            app_config = apps.get_app_config(app.split(".")[-1])
            create_contenttypes(app_config)

    call_command("loaddata", "admin_index", verbosity=0)


class AccountsConfig(AppConfig):
    name = "archiefbeheercomponent.accounts"

    def ready(self):
        post_migrate.connect(update_admin_index, sender=self)
