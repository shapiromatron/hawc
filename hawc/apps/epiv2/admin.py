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


class AdjustmentFactorInline(admin.StackedInline):
    model = AdjustmentFactor
    extra = 0


class ChemicalInline(admin.StackedInline):
    model = Chemical
    extra = 0


class CriteriaInline(admin.StackedInline):
    model = Criteria
    extra = 0


class DataExtractionInline(admin.StackedInline):
    model = DataExtraction
    extra = 0


class ExposureInline(admin.StackedInline):
    model = Exposure
    extra = 0


class ExposureLevelInline(admin.StackedInline):
    model = ExposureLevel
    extra = 0


class OutcomeInline(admin.StackedInline):
    model = Outcome
    extra = 0


class StudyPopulationAdmin(admin.ModelAdmin):
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
