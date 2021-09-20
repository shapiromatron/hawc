from django.contrib import admin
from treebeard.admin import TreeAdmin

from . import forms, models


@admin.register(models.LiteratureAssessment)
class LiteratureAssessmentAdmin(admin.ModelAdmin):
    form = forms.LiteratureAssessmentForm
    readonly_fields = ("assessment", "topic_tsne_refresh_requested", "topic_tsne_last_refresh")
    list_display = (
        "assessment",
        "extraction_tag",
        "topic_tsne_data",
        "topic_tsne_refresh_requested",
        "topic_tsne_last_refresh",
    )
    list_select_related = ("assessment", "extraction_tag")


@admin.register(models.ReferenceFilterTag)
class ReferenceFilterTagAdmin(TreeAdmin):
    pass


@admin.register(models.Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assessment",
        "search_type",
        "source",
        "title",
        "import_file",
        "created",
    )
    list_filter = (
        "search_type",
        "source",
        "assessment",
    )
    search_fields = ("title",)


@admin.register(models.Identifiers)
class IdentifiersAdmin(admin.ModelAdmin):
    list_display = ("unique_id", "database")
    list_filter = ("database",)
    search_fields = ("unique_id",)


@admin.register(models.Reference)
class ReferenceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assessment",
        "title",
        "authors",
        "year",
        "journal",
        "full_text_url",
        "created",
    )
    list_filter = ("year", ("assessment", admin.RelatedOnlyFieldListFilter))
    raw_id_fields = ("searches", "identifiers")
    search_fields = ("title", "authors", "year")
