from django.apps import AppConfig

class EpiConfig(AppConfig):
    name = 'epi'
    verbose_name = 'Epi'

    def ready(self):
        from . import signals
