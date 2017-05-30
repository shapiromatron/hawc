from django.apps import AppConfig

class AssessmentConfig(AppConfig):
    name = 'assessment'
    verbose_name = 'Assessment'

    def ready(self):
        from . import signals
