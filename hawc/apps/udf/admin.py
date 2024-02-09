from django.contrib import admin

from . import models


@admin.register(models.UserDefinedForm)
class UserDefinedFormInline(admin.ModelAdmin):
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
class ModelBindingInline(admin.ModelAdmin):
    list_display = (
        "id",
        "assessment_id",
        "content_type",
        "creator",
        "last_updated",
    )
    list_filter = ("created",)


@admin.register(models.TagBinding)
class TagBindingInline(admin.ModelAdmin):
    list_display = (
        "id",
        "assessment_id",
        "tag_id",
        "creator",
        "last_updated",
    )
    list_filter = ("created",)
    raw_id_fields = ("tag",)
