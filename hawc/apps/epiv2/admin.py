from django.contrib import admin

from . import models


class AdjustmentFactorInline(admin.TabularInline):
    model = models.AdjustmentFactor
    extra = 0


class ChemicalInline(admin.TabularInline):
    model = models.Chemical
    extra = 0


class DataExtractionInline(admin.TabularInline):
    model = models.DataExtraction
    extra = 0


class ExposureInline(admin.TabularInline):
    model = models.Exposure
    extra = 0


class ExposureLevelInline(admin.TabularInline):
    model = models.ExposureLevel
    extra = 0


class OutcomeInline(admin.TabularInline):
    model = models.Outcome
    extra = 0


class DesignAdmin(admin.ModelAdmin):
    search_fields = ("summary", "study__short_citation")
    list_display = (
        "id",
        "summary",
        "study",
        "study_design",
        "created",
        "last_updated",
    )
    list_filter = ("study_design", "created")
    raw_id_fields = ("study",)
    inlines = [
        ChemicalInline,
        ExposureInline,
        ExposureLevelInline,
        OutcomeInline,
        AdjustmentFactorInline,
        DataExtractionInline,
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("study")


admin.site.register(models.Design, DesignAdmin)
admin.site.register(models.AdjustmentFactor)
admin.site.register(models.Chemical)
admin.site.register(models.DataExtraction)
admin.site.register(models.Exposure)
admin.site.register(models.ExposureLevel)
admin.site.register(models.Outcome)
