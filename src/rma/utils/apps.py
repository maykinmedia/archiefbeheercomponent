from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = "rma.utils"

    def ready(self):
        from . import checks  # noqa
