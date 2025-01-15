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
