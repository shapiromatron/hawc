from django.contrib import admin

from .models import (
    AdjustmentFactor,
    AgeProfile,
    Chemical,
    Country,
    Criteria,
    DataExtraction,
    Exposure,
    ExposureLevel,
    MeasurementType,
    Outcome,
    StudyPopulation,
)


class AdjustmentFactorInline(admin.TabularInline):
    model = AdjustmentFactor
    extra = 0


class ChemicalInline(admin.TabularInline):
    model = Chemical
    extra = 0


class CriteriaInline(admin.TabularInline):
    model = Criteria
    extra = 0


class DataExtractionInline(admin.TabularInline):
    model = DataExtraction
    extra = 0


class ExposureInline(admin.TabularInline):
    model = Exposure
    extra = 0


class ExposureLevelInline(admin.TabularInline):
    model = ExposureLevel
    extra = 0


class OutcomeInline(admin.TabularInline):
    model = Outcome
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


admin.site.register(StudyPopulation, StudyPopulationAdmin)
admin.site.register(Country)
admin.site.register(AgeProfile)
admin.site.register(MeasurementType)
admin.site.register(AdjustmentFactor)
admin.site.register(Chemical)
admin.site.register(Criteria)
admin.site.register(DataExtraction)
admin.site.register(Exposure)
admin.site.register(ExposureLevel)
admin.site.register(Outcome)
