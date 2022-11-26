from django.contrib import admin

from ..common.admin import AllListFieldAdmin
from . import models


@admin.register(models.AssessmentSettings)
class AssessmentSettingsAdmin(AllListFieldAdmin):
    list_filter = ("version",)


@admin.register(models.Session)
class SessionAdmin(AllListFieldAdmin):
    list_filter = ("active", "version")
    raw_id_fields = ("endpoint",)
