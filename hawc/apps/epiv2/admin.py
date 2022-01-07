from django.contrib import admin

from .models import (
    AdjustmentFactor,
    Chemical,
    Criteria,
    DataExtraction,
    Exposure,
    ExposureLevel,
    Outcome,
    StudyPopulation,
)


class AdjustmentFactorInline(admin.StackedInline):
    model = AdjustmentFactor
    extra = 1


class ChemicalInline(admin.StackedInline):
    model = Chemical
    extra = 1


class CriteriaInline(admin.StackedInline):
    model = Criteria
    extra = 1


class DataExtractionInline(admin.StackedInline):
    model = DataExtraction
    extra = 1


class ExposureInline(admin.StackedInline):
    model = Exposure
    extra = 1


class ExposureLevelInline(admin.StackedInline):
    model = ExposureLevel
    extra = 1


class OutcomeInline(admin.StackedInline):
    model = Outcome
    extra = 1


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
