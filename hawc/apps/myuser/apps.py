from django.apps import AppConfig


class Config(AppConfig):
    name = "hawc.apps.myuser"
    verbose_name = "Users"

    def ready(self):
        # load signals
        from . import signals  # noqa
