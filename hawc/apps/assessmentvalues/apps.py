from django.apps import AppConfig


class AssessmentvaluesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hawc.apps.assessmentvalues"
    verbose_name = "Assessment Values"

    def ready(self):
        from ..common.models import apply_flavored_help_text

        apply_flavored_help_text(self.name)
        from . import signals  # noqa: F401
