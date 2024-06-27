from django.contrib import admin

from . import models


@admin.register(models.UserDefinedForm)
class UserDefinedFormAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "creator",
        "last_updated",
    )
    list_filter = (
        "deprecated",
        "created",
    )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.ModelBinding)
class ModelBindingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assessment_id",
        "content_type",
        "creator",
        "last_updated",
    )
    list_filter = ("created",)


@admin.register(models.TagBinding)
class TagBindingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assessment_id",
        "tag_id",
        "creator",
        "last_updated",
    )
    list_filter = ("created",)
    raw_id_fields = ("tag",)


@admin.register(models.TagUDFContent)
class TagUDFContentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tag_binding_id",
        "tag_binding",
        "reference_id",
        "reference",
        "created",
        "last_updated",
    )
    list_filter = ("last_updated",)
    raw_id_fields = ("reference",)
    readonly_fields = ("reference", "tag_binding", "created", "last_updated")


@admin.register(models.ModelUDFContent)
class ModelUDFContentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "model_binding_id",
        "model_binding",
        "content_type",
        "object_id",
        "content_object",
        "created",
        "last_updated",
    )
    list_filter = ("last_updated",)
    readonly_fields = ("content_type", "object_id", "model_binding", "created", "last_updated")
