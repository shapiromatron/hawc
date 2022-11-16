from django.contrib import admin

from ..common.admin import AllListFieldAdmin
from . import models


@admin.register(models.AssessmentSettings)
class AssessmentSettingsAdmin(AllListFieldAdmin):
    list_filter = ("version",)


class ModelAdmin(admin.TabularInline):
    model = models.Model
    fk_name = "session"
    extra = 0


@admin.register(models.Session)
class SessionAdmin(AllListFieldAdmin):
    list_filter = ("version",)
    raw_id_fields = ("endpoint",)
    inlines = [ModelAdmin]


@admin.register(models.SelectedModel)
class SelectedModelAdmin(AllListFieldAdmin):
    raw_id_fields = ("endpoint", "model")
    list_select_related = ("endpoint", "model")
