from django.apps import AppConfig


class AssessmentConfig(AppConfig):
    name = "hawc.apps.assessment"
    verbose_name = "Assessment"

    def ready(self):
        from ..utils.models import apply_flavored_help_text

        apply_flavored_help_text(self.name)
        from . import signals  # noqa: F401
