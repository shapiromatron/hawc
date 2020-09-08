from django.apps import AppConfig
from django.conf import settings


class LitConfig(AppConfig):
    name = "hawc.apps.lit"
    verbose_name = "Literature"

    def ready(self):
        from . import signals  # noqa
        from ...services.epa import pubmed

        if settings.PUBMED_API_KEY:
            pubmed.connect(settings.PUBMED_API_KEY)
