from selectable.registry import registry

from utils.lookups import DistinctStringLookup, RelatedLookup

from . import models


class StudyPopulationByStudyLookup(RelatedLookup):
    # Return names of study populations available for a particular study
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


class EffectLookup(DistinctStringLookup):
    model = models.Outcome
    distinct_field = "effect"


registry.register(StudyPopulationByStudyLookup)
registry.register(RegionLookup)
registry.register(StateLookup)
registry.register(CriteriaLookup)
registry.register(AdjustmentFactorLookup)
registry.register(EffectLookup)
