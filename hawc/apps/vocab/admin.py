from django.contrib import admin

from . import models


class TermRelationAdmin(admin.TabularInline):
    fk_name = "term"
    model = models.TermRelation
    extra = 1


@admin.register(models.Term)
class TermAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "namespace",
        "type",
        "name",
        "deprecated_on",
        "created_on",
        "last_updated",
    )
    list_filter = (
        "namespace",
        "type",
    )
    search_fields = ("name",)
    inlines = (TermRelationAdmin,)


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
