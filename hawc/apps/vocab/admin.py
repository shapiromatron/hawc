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
    search_fields = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("entities")

    def get_entities(self, obj):
        return ul_items(obj.entities.all(), lambda el: f"<a href={el.get_external_url()}>{el}</a>")

    get_entities.short_description = "Related entities"
    get_entities.allow_tags = True


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

    def get_uid(self, obj):
        return format_html(f"<a href='{obj.get_external_url()}'>{obj.uid}</a>")

    get_uid.short_description = "UID"
    get_uid.allow_tags = True

    def get_terms(self, obj):
        return ul_items(obj.terms.all(), lambda el: f"<a href={el.get_admin_edit_url()}>{el}</a>")

    get_terms.short_description = "Related terms"
    get_terms.allow_tags = True
