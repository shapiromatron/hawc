from django.contrib import admin
from django.utils.html import format_html
from reversion.admin import VersionAdmin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

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
    raw_id_fields = ("endpoints", "studies")

    @admin.display(description="URL")
    def show_url(self, obj):
        return format_html(f"<a href='{obj.get_absolute_url()}'>{obj.id}</a>")


@admin.register(models.DataPivotUpload, models.DataPivotQuery)
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
    list_filter = ("published", ("assessment", admin.RelatedOnlyFieldListFilter))
    search_fields = ("assessment__name", "title")

    @admin.display(description="URL")
    def show_url(self, obj):
        return format_html(f"<a href='{obj.get_absolute_url()}'>{obj.id}</a>")


@admin.register(models.SummaryText)
class SummaryTextAdmin(TreeAdmin):
    list_display = (
        "title",
        "created",
    )
    form = movenodeform_factory(models.SummaryText)


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
