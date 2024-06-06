from django.apps import AppConfig


class FormLibraryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hawc.apps.udf"
    verbose_name = "User Defined Fields"

    def ready(self):
        from . import signals  # noqa: F401
