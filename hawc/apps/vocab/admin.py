from django.contrib import admin
from django.utils.html import format_html

from . import models


def ul_items(qs, method):
    elements = [f"<li>{method(item)}</li>" for item in qs]
    return format_html(f'<ul>{" ".join(elements)}</ul')


@admin.register(models.Term)
class TermAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uid",
        "namespace",
        "type",
        "name",
        "parent",
        "get_entities",
        "deprecated_on",
        "created_on",
        "last_updated",
    )
    list_filter = (
        "namespace",
        "type",
    )
    list_select_related = ("parent",)
    search_fields = ("name", "uid")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("entities")

    @admin.display(description="Related entities")
    def get_entities(self, obj):
        return ul_items(obj.entities.all(), lambda el: f"<a href={el.get_external_url()}>{el}</a>")

    def has_delete_permission(self, request, obj=None):
        return False


class EntityTermRelationAdmin(admin.TabularInline):
    model = models.EntityTermRelation
    extra = 1
    raw_id_fields = ("term",)


@admin.register(models.Entity)
class EntityAdmin(admin.ModelAdmin):
    inlines = (EntityTermRelationAdmin,)
    list_display = (
        "ontology",
        "get_uid",
        "get_terms",
        "deprecated_on",
        "created_on",
        "last_updated",
    )
    list_filter = ("ontology",)
    search_fields = ("uid",)
    inlines = (EntityTermRelationAdmin,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("terms")

    @admin.display(description="UID")
    def get_uid(self, obj):
        return format_html(f"<a href='{obj.get_external_url()}'>{obj.uid}</a>")

    @admin.display(description="Related terms")
    def get_terms(self, obj):
        return ul_items(obj.terms.all(), lambda el: f"<a href={el.get_admin_edit_url()}>{el}</a>")


@admin.register(models.GuidelineProfile)
class GuidelineProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "guideline_id",
        "endpoint",
        "obs_status",
        "description",
    )
    list_filter = ("guideline_id", "obs_status")
    search_fields = ("guideline id", "obs_status")
