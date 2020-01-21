from django.apps import AppConfig


class RiskOfBiasConfig(AppConfig):
    name = "hawc.apps.riskofbias"
    verbose_name = "Risk of Bias"

    def ready(self):
        from ..common.models import apply_flavored_help_text

        apply_flavored_help_text(self.name)
        from . import signals  # noqa
