from django.apps import AppConfig

class StudyConfig(AppConfig):
    name = 'study'
    verbose_name = 'Study'

    def ready(self):
        from . import signals
