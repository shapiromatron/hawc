from django.apps import AppConfig
from django.conf import settings


class AnimalConfig(AppConfig):
    name = 'animal'
    verbose_name = 'Animal'

    def ready(self):
        from utils.models import apply_flavored_help_text
        apply_flavored_help_text(self.name)
        from . import signals
