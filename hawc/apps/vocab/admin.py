from django.contrib import admin

from . import models


@admin.register(models.Term)
class TermAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uid",
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
    search_fields = ("name", "uid")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("entities")

    def has_delete_permission(self, request, obj=None):
        return False


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
