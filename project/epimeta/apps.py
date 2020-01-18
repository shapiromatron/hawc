from django.apps import AppConfig


class EpimetaConfig(AppConfig):
    name = "epimeta"
    verbose_name = "EpiMeta"

    def ready(self):
        from . import signals  # noqa: F401
