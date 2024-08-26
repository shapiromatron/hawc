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
        "notes",
        "due_date",
        "started",
        "completed",
    )
    list_select_related = ("study", "owner", "type", "status")


@admin.register(models.TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    search_fields = (
        "owner__email",
        "owner__last_name",
    )
    list_display = (
        "assessment",
        "name",
        "order",
        "description",
        "created",
        "last_updated",
    )


@admin.register(models.TaskStatus)
class TaskStatusAdmin(admin.ModelAdmin):
    search_fields = (
        "owner__email",
        "owner__last_name",
    )
    list_display = (
        "assessment",
        "name",
        "value",
        "description",
        "order",
        "color",
        "terminal_status",
        "created",
        "last_updated",
    )


@admin.register(models.TaskTrigger)
class TaskTriggerAdmin(admin.ModelAdmin):
    search_fields = (
        "owner__email",
        "owner__last_name",
    )
    list_display = (
        "task_type",
        "current_status",
        "next_status",
        "event",
        "created",
        "last_updated",
    )
    list_select_related = ("task_type", "current_status", "next_status")
