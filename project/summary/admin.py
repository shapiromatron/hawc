from django.contrib import admin

from . import models


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


class DataPivotAdmin(admin.ModelAdmin):
    list_display = ("__str__", "assessment_id", "assessment", "published", "created")
    list_filter = ("published",)
    search_fields = ("assessment__name", "title")


admin.site.register(models.Visual, VisualAdmin)
admin.site.register(models.DataPivotUpload, DataPivotAdmin)
admin.site.register(models.DataPivotQuery, DataPivotAdmin)
