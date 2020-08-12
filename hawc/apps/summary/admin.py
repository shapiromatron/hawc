from django.contrib import admin
from django.utils.html import format_html

from . import models


@admin.register(models.Visual)
class VisualAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "show_url",
        "assessment_id",
        "assessment",
        "visual_type",
        "published",
        "created",
    )

    list_filter = ("visual_type", "published", ("assessment", admin.RelatedOnlyFieldListFilter))
    search_fields = ("assessment__name", "title")

    def show_url(self, obj):
        return format_html(f"<a href='{obj.get_absolute_url()}'>{obj.id}</a>")

    show_url.short_description = "URL"


@admin.register(models.DataPivotUpload, models.DataPivotQuery)
class DataPivotAdmin(admin.ModelAdmin):
    list_display = ("title", "show_url", "assessment_id", "assessment", "published", "created")
    list_filter = ("published", ("assessment", admin.RelatedOnlyFieldListFilter))
    search_fields = ("assessment__name", "title")

    def show_url(self, obj):
        return format_html(f"<a href='{obj.get_absolute_url()}'>{obj.id}</a>")

    show_url.short_description = "URL"
