from django.apps import AppConfig


class AnimalConfig(AppConfig):
    name = "hawc.apps.animal"
    verbose_name = "Animal"

    def ready(self):
        from ..utils.models import apply_flavored_help_text

        apply_flavored_help_text(self.name)
        from . import signals  # noqa: F401
