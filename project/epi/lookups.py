from selectable.registry import registry

from utils.lookups import DistinctStringLookup, RelatedLookup

from . import models


class StudyPopulationByAssessmentLookup(RelatedLookup):
    model = models.StudyPopulation
    search_fields = ('name__icontains', )
    related_filter = 'study__assessment_id'

    def get_query(self, request, term):
        return super(StudyPopulationByAssessmentLookup, self)\
            .get_query(request, term)\
            .distinct('name')


class StudyPopulationByStudyLookup(RelatedLookup):
    model = models.StudyPopulation
    search_fields = ('name__icontains', )
    related_filter = 'study_id'


class RegionLookup(DistinctStringLookup):
    model = models.StudyPopulation
    distinct_field = "region"


class StateLookup(DistinctStringLookup):
    model = models.StudyPopulation
    distinct_field = "state"


class CriteriaLookup(RelatedLookup):
    model = models.Criteria
    search_fields = ('description__icontains', )
    related_filter = 'assessment_id'


class AdjustmentFactorLookup(RelatedLookup):
    model = models.AdjustmentFactor
    search_fields = ('description__icontains', )
    related_filter = 'assessment_id'


class ComparisonSetByStudyPopulationLookup(RelatedLookup):
    model = models.ComparisonSet
    search_fields = ('name__icontains', )
    related_filter = 'study_population_id'


class ComparisonSetByOutcomeLookup(ComparisonSetByStudyPopulationLookup):
    related_filter = 'outcome_id'


class ExposureByStudyPopulationLookup(RelatedLookup):
    model = models.Exposure
    search_fields = ('name__icontains', )
    related_filter = 'study_population_id'


class ExposureMeasuredLookup(DistinctStringLookup):
    model = models.Exposure
    distinct_field = "measured"


class ExposureMetricLookup(DistinctStringLookup):
    model = models.Exposure
    distinct_field = "metric"


class AgeOfExposureLookup(DistinctStringLookup):
    model = models.Exposure
    distinct_field = "age_of_exposure"


class OutcomeLookup(RelatedLookup):
    model = models.Outcome
    search_fields = ('name__icontains', )
    related_filter = 'assessment_id'


class OutcomeByStudyPopulationLookup(RelatedLookup):
    model = models.Outcome
    search_fields = ('name__icontains', )
    related_filter = 'study_population_id'


class SystemLookup(DistinctStringLookup):
    model = models.Outcome
    distinct_field = "system"


class EffectLookup(DistinctStringLookup):
    model = models.Outcome
    distinct_field = "effect"


class EffectSubtypeLookup(DistinctStringLookup):
    model = models.Outcome
    distinct_field = "effect_subtype"


class AgeOfMeasurementLookup(DistinctStringLookup):
    model = models.Outcome
    distinct_field = "age_of_measurement"


class ResultByOutcomeLookup(RelatedLookup):
    model = models.Result
    search_fields = (
        'metric__metric__icontains',
        'comparison_set__name__icontains'
    )
    related_filter = 'outcome_id'


registry.register(StudyPopulationByAssessmentLookup)
registry.register(StudyPopulationByStudyLookup)
registry.register(RegionLookup)
registry.register(StateLookup)
registry.register(CriteriaLookup)
registry.register(AdjustmentFactorLookup)
registry.register(ExposureByStudyPopulationLookup)
registry.register(ExposureMeasuredLookup)
registry.register(ExposureMetricLookup)
registry.register(AgeOfExposureLookup)
registry.register(ComparisonSetByStudyPopulationLookup)
registry.register(ComparisonSetByOutcomeLookup)
registry.register(OutcomeLookup)
registry.register(OutcomeByStudyPopulationLookup)
registry.register(SystemLookup)
registry.register(EffectLookup)
registry.register(EffectSubtypeLookup)
registry.register(AgeOfMeasurementLookup)
registry.register(ResultByOutcomeLookup)
