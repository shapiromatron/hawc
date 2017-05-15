

from django.apps import AppConfig


class RiskOfBiasConfig(AppConfig):
    name = 'riskofbias'
    verbose_name = 'Risk of Bias'

    def ready(self):
        from . import signals  # noqa
