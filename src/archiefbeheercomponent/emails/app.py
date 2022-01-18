from django.apps import AppConfig


class EmailPreferenceConfig(AppConfig):
    name = "archiefbeheercomponent.emails"

    def ready(self):
        # load the signal receivers
        from . import signals  # noqa
