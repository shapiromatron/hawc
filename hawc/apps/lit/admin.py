from django.contrib import admin
from treebeard.admin import TreeAdmin

from ..study.models import Study
from . import forms, models


@admin.register(models.LiteratureAssessment)
class LiteratureAssessmentAdmin(admin.ModelAdmin):
    form = forms.LiteratureAssessmentForm
    readonly_fields = ("assessment",)
    list_display = (
        "assessment_id",
        "conflict_resolution",
        "extraction_tag",
    )
    list_filter = ("conflict_resolution",)
    list_select_related = ("extraction_tag",)


@admin.register(models.ReferenceFilterTag)
class ReferenceFilterTagAdmin(TreeAdmin):
    readonly_fields = ("path", "depth", "numchild")


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
    can_delete = False
    extra = 0
    model = models.Reference.identifiers.through
    readonly_fields = ("reference",)
    verbose_name = "Reference"
    verbose_name_plural = "Related references"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("reference")


class StudiesInline(admin.StackedInline):
    can_delete = False
    exclude = ("reference",)
    extra = 0
    model = Study.identifiers.through
    readonly_fields = ("identifiers",)
    verbose_name = "Study"
    verbose_name_plural = "Related studies"

    def get_queryset(self, request):
        return Study.objects.all()


@admin.register(models.Identifiers)
class IdentifiersAdmin(admin.ModelAdmin):
    list_display = ("unique_id", "database")
    list_filter = ("database",)
    search_fields = ("unique_id",)
    inlines = (ReferencesInline, StudiesInline)


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


@admin.register(models.UserReferenceTag)
class UserReferenceTagAdmin(admin.ModelAdmin):
    raw_id_fields = ("reference",)
    list_display = ("id", "user", "reference", "created", "last_updated")
    list_filter = ("last_updated",)
    list_select_related = ("user", "reference")
    readonly_fields = ("created", "last_updated")
