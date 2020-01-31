from django.contrib import admin

from . import models


@admin.register(models.Visual)
class VisualAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "assessment_id",
        "assessment",
        "visual_type",
        "published",
        "created",
    )
    list_filter = ("visual_type", "published")
    search_fields = ("assessment__name", "title")


@admin.register(models.DataPivotUpload, models.DataPivotQuery)
class DataPivotAdmin(admin.ModelAdmin):
    list_display = ("__str__", "assessment_id", "assessment", "published", "created")
    list_filter = ("published",)
    search_fields = ("assessment__name", "title")
