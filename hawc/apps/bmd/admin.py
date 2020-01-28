from django.contrib import admin

from ..common.admin import AllListFieldAdmin
from . import models


@admin.register(models.AssessmentSettings)
class AssessmentSettingsAdmin(AllListFieldAdmin):
    pass


@admin.register(models.LogicField)
class LogicFieldAdmin(AllListFieldAdmin):
    pass


@admin.register(models.Session)
class SessionAdmin(AllListFieldAdmin):
    pass


@admin.register(models.Model)
class ModelAdmin(AllListFieldAdmin):
    pass


@admin.register(models.SelectedModel)
class SelectedModelAdmin(AllListFieldAdmin):
    pass
