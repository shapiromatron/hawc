from django.contrib import admin

from utils.admin import AllListFieldAdmin
from . import models


class AssessmentSettingsAdmin(AllListFieldAdmin):
    pass


class LogicFieldAdmin(AllListFieldAdmin):
    pass


class SessionAdmin(AllListFieldAdmin):
    pass


class ModelAdmin(AllListFieldAdmin):
    pass


class SelectedModelAdmin(AllListFieldAdmin):
    pass


admin.site.register(models.AssessmentSettings, AssessmentSettingsAdmin)
admin.site.register(models.LogicField, LogicFieldAdmin)
admin.site.register(models.Session, SessionAdmin)
admin.site.register(models.Model, ModelAdmin)
admin.site.register(models.SelectedModel, SelectedModelAdmin)
