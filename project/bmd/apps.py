from django.apps import AppConfig


class BMDConfig(AppConfig):
    name = 'bmd'
    verbose_name = 'Benchmark dose modeling'

    def ready(self):
        import signals
