from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = "archiefvernietingscomponent.utils"

    def ready(self):
        from . import checks  # noqa
