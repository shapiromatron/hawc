from django.apps import AppConfig


class EpiConfig(AppConfig):
    name = "hawc.apps.epi"
    verbose_name = "Epi"

    def ready(self):
        from ..utils.models import apply_flavored_help_text

        apply_flavored_help_text(self.name)
        from . import signals  # noqa: F401
