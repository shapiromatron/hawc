from django.contrib import admin

from . import models


@admin.register(models.Term)
class TermAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "namespace",
        "type",
        "name",
        "parent",
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


class EntityTermRelationAdmin(admin.TabularInline):
    model = models.EntityTermRelation
    extra = 1


@admin.register(models.Entity)
class EntityAdmin(admin.ModelAdmin):
    inlines = (EntityTermRelationAdmin,)
    list_display = (
        "ontology",
        "uid",
        "deprecated_on",
        "created_on",
        "last_updated",
    )
    list_filter = ("ontology",)
    search_fields = ("uid",)
    inlines = (EntityTermRelationAdmin,)
