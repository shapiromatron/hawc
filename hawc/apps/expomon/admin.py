from django.contrib import admin

from . import models


class ChemicalInline(admin.TabularInline):
    model = models.Chemical
    extra = 0


class LocationInline(admin.TabularInline):
    model = models.Location
    extra = 0


class AmbientAirMediaInline(admin.TabularInline):
    model = models.AmbientAirMedia
    extra = 0

class SedimentMediaInline(admin.TabularInline):
    model = models.SedimentMedia
    extra = 0


class ExtractionAdmin(admin.ModelAdmin):
    search_fields = ("study__short_citation",)
    list_display = (
        "id",
        "brief_description",
        "study",
    )
    # list_filter = ("study_design", "created")
    # raw_id_fields = ("study",)
    inlines = [
        ChemicalInline,
        LocationInline,
        AmbientAirMediaInline,
        SedimentMediaInline,
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("study")


admin.site.register(models.Extraction, ExtractionAdmin)
admin.site.register(models.Chemical)
admin.site.register(models.Location)
admin.site.register(models.AmbientAirMedia)
admin.site.register(models.SedimentMedia)
