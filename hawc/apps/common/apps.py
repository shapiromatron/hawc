from django.apps import AppConfig


class CommonConfig(AppConfig):
    name = "hawc.apps.common"

    def ready(self):
        from . import autocomplete

        autocomplete.autodiscover()
