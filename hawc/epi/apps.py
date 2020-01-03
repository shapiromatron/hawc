from django.apps import AppConfig

class EpiConfig(AppConfig):
    name = 'epi'
    verbose_name = 'Epi'

    def ready(self):
        from utils.models import apply_flavored_help_text
        apply_flavored_help_text(self.name)
        from . import signals
