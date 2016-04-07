from __future__ import unicode_literals

from django.apps import AppConfig


class RiskOfBiasConfig(AppConfig):
    name = 'riskofbias'
    verbose_name = 'Risk of Bias'

    def ready(self):
        import signals
