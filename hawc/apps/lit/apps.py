from django.apps import AppConfig


class LitConfig(AppConfig):
    name = "hawc.apps.lit"
    verbose_name = "Literature"

    def ready(self):
        from . import signals  # noqa
