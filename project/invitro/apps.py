from django.apps import AppConfig


class InvitroConfig(AppConfig):
    name = "invitro"
    verbose_name = "Invitro"

    def ready(self):
        from . import signals  # noqa: F401
