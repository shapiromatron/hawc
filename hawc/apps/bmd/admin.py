from django.contrib import admin

from ..common.admin import AllListFieldAdmin
from . import models


@admin.register(models.AssessmentSettings)
class AssessmentSettingsAdmin(AllListFieldAdmin):
    list_filter = ("version",)


@admin.register(models.Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("id", "date_executed", "selected", "created", "last_updated")
    list_filter = ("active", "version", "date_executed")
    raw_id_fields = ("endpoint",)
