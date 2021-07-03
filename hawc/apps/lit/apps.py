from django.apps import AppConfig
from django.conf import settings


class LitConfig(AppConfig):
    name = "hawc.apps.lit"
    verbose_name = "Literature"

    def ready(self):
        from ...services.nih import pubmed
        from . import signals  # noqa

        if settings.PUBMED_API_KEY:
            pubmed.connect(settings.PUBMED_API_KEY)
