from django.apps import AppConfig


class AnimalConfig(AppConfig):
    name = "hawc.apps.animal"
    verbose_name = "Animal"

    def ready(self):
        from . import signals  # noqa: F401
