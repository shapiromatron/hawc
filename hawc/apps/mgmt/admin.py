from django.contrib import admin

from . import models


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    search_fields = (
        "owner__email",
        "owner__last_name",
    )
    list_display = (
        "study",
        "type",
        "owner",
        "status",
        "open",
        "due_date",
        "started",
        "completed",
    )
    list_select_related = ("study", "owner")
