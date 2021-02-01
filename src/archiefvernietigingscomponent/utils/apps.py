from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = "archiefvernietigingscomponent.utils"

    def ready(self):
        from . import checks  # noqa
