from django.apps import AppConfig


class RiskOfBiasConfig(AppConfig):
    name = 'riskofbias'
    verbose_name = 'Study Evaluation'

    def ready(self):
        from . import signals  # noqa
