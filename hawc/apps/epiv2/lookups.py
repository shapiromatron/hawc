from selectable.registry import registry

from ..common.lookups import RelatedDistinctStringLookup
from . import models


class OutcomeByDesignLookup(RelatedDistinctStringLookup):
    model = models.Outcome
    distinct_field = "endpoint"
    related_filter = "design_id"


class OutcomeByHealthOutcome(RelatedDistinctStringLookup):
    model = models.Outcome
    distinct_field = "health_outcome"
    related_filter = "design_id"


registry.register(OutcomeByDesignLookup)
registry.register(OutcomeByHealthOutcome)
