from django.apps import AppConfig

class StudyConfig(AppConfig):
    name = 'study'
    verbose_name = 'Study'

    def ready(self):
        from utils.models import apply_flavored_help_text
        apply_flavored_help_text(self.name)
        from . import signals
