from django.apps import AppConfig

class AnimalConfig(AppConfig):
    name = 'animal'
    verbose_name = 'Animal'

    def ready(self):
        from . import signals
