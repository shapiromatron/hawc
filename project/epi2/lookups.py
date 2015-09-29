from selectable.registry import registry

from utils.lookups import DistinctStringLookup, RelatedLookup

from . import models


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


class ComparisonGroupsByStudyPopulationLookup(RelatedLookup):
    model = models.ComparisonGroups
    search_fields = ('name__icontains', )
    related_filter = 'study_population_id'


class ComparisonGroupsByOutcomeLookup(ComparisonGroupsByStudyPopulationLookup):
    related_filter = 'outcome_id'


class ExposureByStudyPopulationLookup(RelatedLookup):
    model = models.Exposure2
    search_fields = ('name__icontains', )
    related_filter = 'study_population_id'


class OutcomeByStudyPopulationLookup(RelatedLookup):
    model = models.Outcome
    search_fields = ('name__icontains', )
    related_filter = 'study_population_id'


class EffectLookup(DistinctStringLookup):
    model = models.Outcome
    distinct_field = "effect"


class SystemLookup(DistinctStringLookup):
    model = models.Outcome
    distinct_field = "system"


class ResultByOutcomeLookup(RelatedLookup):
    model = models.Result
    search_fields = ('metric__metric__icontains', 'groups__name__icontains')
    related_filter = 'outcome_id'


registry.register(StudyPopulationByStudyLookup)
registry.register(RegionLookup)
registry.register(StateLookup)
registry.register(CriteriaLookup)
registry.register(AdjustmentFactorLookup)
registry.register(ExposureByStudyPopulationLookup)
registry.register(ComparisonGroupsByStudyPopulationLookup)
registry.register(ComparisonGroupsByOutcomeLookup)
registry.register(OutcomeByStudyPopulationLookup)
registry.register(EffectLookup)
registry.register(SystemLookup)
registry.register(ResultByOutcomeLookup)
