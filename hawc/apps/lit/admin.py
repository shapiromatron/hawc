from django.contrib import admin
from treebeard.admin import TreeAdmin

from ..study.models import Study
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


class ReferencesInline(admin.StackedInline):
    def get_queryset(self, request):
        qs = super(ReferencesInline, self).get_queryset(request)
        return qs.select_related("reference")

    model = models.Reference.identifiers.through
    readonly_fields = ("reference",)
    extra = 0
    can_delete = False
    verbose_name = "Ref"
    verbose_name_plural = "Reference-identifier relationships"


class StudiesInline(admin.StackedInline):
    def get_queryset(self, request):
        return Study.objects.all()

    model = Study.identifiers.through
    readonly_fields = ("identifiers",)
    extra = 0
    can_delete = False
    exclude = ("reference",)
    verbose_name = "Study"
    verbose_name_plural = "Study-identifier relationships"


@admin.register(models.Identifiers)
class IdentifiersAdmin(admin.ModelAdmin):
    list_display = ("unique_id", "database")
    list_filter = ("database",)
    search_fields = ("unique_id",)
    inlines = (
        ReferencesInline,
        StudiesInline,
    )


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
