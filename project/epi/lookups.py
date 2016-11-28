from selectable.registry import registry

from utils.lookups import (DistinctStringLookup, RelatedLookup,
                           RelatedDistinctStringLookup)

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


class RelatedStudyPopulationAgeProfileLookup(RelatedDistinctStringLookup):
    model = models.StudyPopulation
    distinct_field = 'age_profile'
    related_filter = 'study__assessment_id'


class RelatedStudyPopulationSourceLookup(RelatedDistinctStringLookup):
    model = models.StudyPopulation
    distinct_field = 'source'
    related_filter = 'study__assessment_id'


class RelatedCountryNameLookup(RelatedDistinctStringLookup):
    model = models.Country
    distinct_field = 'name'
    related_filter = 'studypopulation__study__assessment_id'


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


class RelatedExposureMetricLookup(RelatedDistinctStringLookup):
    model = models.Exposure
    distinct_field = "metric"
    related_filter = 'study_population__study__assessment_id'


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


class RelatedSystemLookup(RelatedDistinctStringLookup):
    model = models.Outcome
    distinct_field = "system"
    related_filter = 'assessment_id'


class RelatedEffectLookup(RelatedDistinctStringLookup):
    model = models.Outcome
    distinct_field = "effect"
    related_filter = 'assessment_id'


class RelatedEffectSubtypeLookup(RelatedDistinctStringLookup):
    model = models.Outcome
    distinct_field = "effect_subtype"
    related_filter = 'assessment_id'


class ResultByOutcomeLookup(RelatedLookup):
    model = models.Result
    search_fields = (
        'metric__metric__icontains',
        'comparison_set__name__icontains'
    )
    related_filter = 'outcome_id'


registry.register(StudyPopulationByAssessmentLookup)
registry.register(StudyPopulationByStudyLookup)
registry.register(RelatedStudyPopulationAgeProfileLookup)
registry.register(RelatedStudyPopulationSourceLookup)
registry.register(RelatedCountryNameLookup)
registry.register(RegionLookup)
registry.register(StateLookup)
registry.register(CriteriaLookup)
registry.register(AdjustmentFactorLookup)
registry.register(ExposureByStudyPopulationLookup)
registry.register(ExposureMeasuredLookup)
registry.register(ExposureMetricLookup)
registry.register(RelatedExposureMetricLookup)
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
