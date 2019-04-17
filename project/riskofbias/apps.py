from django.apps import AppConfig


class RiskOfBiasConfig(AppConfig):
    name = 'riskofbias'
    verbose_name = 'Risk of Bias'

    def ready(self):
        from utils.models import apply_flavored_help_text
        apply_flavored_help_text(self.name)
        from . import signals  # noqa
