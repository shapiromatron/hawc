from django.apps import AppConfig


class HawcAdminConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hawc.apps.hawc_admin"

    def ready(self) -> None:
        from wagtail.admin.views.account import NameEmailSettingsPanel

        NameEmailSettingsPanel.is_active = lambda self: False
        return super().ready()
