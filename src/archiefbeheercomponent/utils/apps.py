from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = "archiefbeheercomponent.utils"

    def ready(self):
        from . import checks  # noqa
