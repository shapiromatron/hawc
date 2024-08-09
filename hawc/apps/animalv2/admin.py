from django.contrib import admin
from reversion.admin import VersionAdmin

from . import models


@admin.register(models.StudyLevelValue)
class StudyValuesAdmin(VersionAdmin, admin.ModelAdmin):
    list_display = ("id", "study", "system", "value_type", "value", "comments")
    list_filter = ("system", "value_type")
    search_fields = ("study", "comments", "system", "value_type")
