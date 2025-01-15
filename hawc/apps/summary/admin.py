from django.contrib import admin
from django.utils.html import format_html
from reversion.admin import VersionAdmin

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
        "last_updated",
    )

    list_filter = ("visual_type", "published", ("assessment", admin.RelatedOnlyFieldListFilter))
    search_fields = ("assessment__name", "title")
    raw_id_fields = ("endpoints",)

    @admin.display(description="URL")
    def show_url(self, obj):
        return format_html("<a href='{}'>{}</a>", obj.get_absolute_url(), obj.id)


class DataPivotAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "show_url",
        "assessment_id",
        "assessment",
        "published",
        "created",
        "last_updated",
    )
    list_filter = ("published", ("evidence_type", admin.RelatedOnlyFieldListFilter))
    search_fields = ("assessment__name", "title")

    @admin.display(description="URL")
    def show_url(self, obj):
        return format_html("<a href='{}'>{}</a>", obj.get_absolute_url(), obj.id)


class DataPivotQueryAdmin(DataPivotAdmin):
    list_filter = ("published", "evidence_type")


@admin.register(models.SummaryTable)
class SummaryTableAdmin(VersionAdmin):
    list_display = (
        "title",
        "assessment_id",
        "assessment",
        "table_type",
        "published",
        "created",
    )

    list_filter = ("table_type", "published", ("assessment", admin.RelatedOnlyFieldListFilter))


admin.site.register(models.DataPivotUpload, DataPivotAdmin)
admin.site.register(models.DataPivotQuery, DataPivotQueryAdmin)
