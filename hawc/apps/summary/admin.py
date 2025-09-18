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
    show_facets = admin.ShowFacets.ALWAYS
    readonly_fields = ("dp_id", "dp_slug")

    @admin.display(description="URL")
    def show_url(self, obj):
        return format_html("<a href='{}'>{}</a>", obj.get_absolute_url(), obj.id)


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
    show_facets = admin.ShowFacets.ALWAYS
