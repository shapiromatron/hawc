from django.apps import AppConfig
from django.conf import settings


class LitConfig(AppConfig):
    name = "hawc.apps.lit"
    verbose_name = "Literature"

    def ready(self):
        from . import signals  # noqa
        from litter_getter import pubmed

        pubmed.connect(settings.PUBMED_TOOL, settings.PUBMED_EMAIL)
