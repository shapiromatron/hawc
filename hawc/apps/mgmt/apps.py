from django.apps import AppConfig


class MgmtConfig(AppConfig):
    name = "hawc.apps.mgmt"
    verbose_name = "Project management"

    def ready(self):
        from . import signals  # noqa: F401
