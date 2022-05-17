from selectable.registry import registry

from ..common.lookups import RelatedDistinctStringLookup
from . import models


class RelatedCauseLookup(RelatedDistinctStringLookup):
    model = models.Cause
    distinct_field = "name"
    related_filter = "study__assessment_id"


class RelatedEffectLookup(RelatedDistinctStringLookup):
    model = models.Effect
    distinct_field = "name"
    related_filter = "study__assessment_id"


registry.register(RelatedCauseLookup)
registry.register(RelatedEffectLookup)
