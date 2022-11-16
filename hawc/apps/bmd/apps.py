from django.apps import AppConfig


class BMDConfig(AppConfig):
    name = "hawc.apps.bmd"
    verbose_name = "Benchmark dose modeling"

    def ready(self):
        # load signals
        from . import signals  # noqa
