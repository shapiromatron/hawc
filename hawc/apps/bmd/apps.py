from django.apps import AppConfig


class BMDConfig(AppConfig):
    name = "hawc.apps.bmd"
    verbose_name = "Benchmark dose modeling"

    def ready(self):
        from . import signals  # noqa
