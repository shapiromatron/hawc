from django.contrib import admin

from . import models


class ChemicalInline(admin.TabularInline):
    model = models.Chemical
    extra = 0


class ExperimentAdmin(admin.ModelAdmin):
    search_fields = ("name", "description", "study__short_citation")
    list_display = (
        "id",
        "name",
        "study",
        "created",
        "last_updated",
    )
    list_filter = ("created",)
    raw_id_fields = ("study",)
    inlines = [
        ChemicalInline,
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("study")


admin.site.register(models.Experiment, ExperimentAdmin)
admin.site.register(models.Chemical)
