from django.apps import AppConfig


class MaterializedViewsConfig(AppConfig):
    name = "hawc.apps.materialized"
    verbose_name = "Materialized Views"

    def ready(self):
        from . import signals  # noqa
