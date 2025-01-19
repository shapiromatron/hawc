from django.contrib import admin
from reversion.admin import VersionAdmin

from . import models


@admin.register(models.StudyLevelValue)
class StudyValuesAdmin(VersionAdmin, admin.ModelAdmin):
    list_display = ("id", "study", "system", "value_type", "value", "units")
    list_filter = ("system", "value_type")
    list_select_related = ("units",)
    search_fields = ("study__short_citation", "system")
