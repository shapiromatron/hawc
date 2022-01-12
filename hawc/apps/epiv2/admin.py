from django.contrib import admin

from . import models


class AdjustmentFactorInline(admin.TabularInline):
    model = models.AdjustmentFactor
    extra = 0


class ChemicalInline(admin.TabularInline):
    model = models.Chemical
    extra = 0


class CriteriaInline(admin.TabularInline):
    model = models.Criteria
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


class StudyPopulationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "summary",
        "study",
        "study_design",
        "created",
        "last_updated",
    )
    inlines = [
        CriteriaInline,
        ChemicalInline,
        ExposureInline,
        ExposureLevelInline,
        OutcomeInline,
        AdjustmentFactorInline,
        DataExtractionInline,
    ]


admin.site.register(models.StudyPopulationV2, StudyPopulationAdmin)
admin.site.register(models.AgeProfile)
admin.site.register(models.MeasurementType)
admin.site.register(models.AdjustmentFactor)
admin.site.register(models.Chemical)
admin.site.register(models.Criteria)
admin.site.register(models.DataExtraction)
admin.site.register(models.Exposure)
admin.site.register(models.ExposureLevel)
admin.site.register(models.Outcome)
