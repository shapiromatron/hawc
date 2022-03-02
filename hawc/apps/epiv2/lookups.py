from selectable.registry import registry

from hawc.apps.epi.models import Country

from ..common.lookups import DistinctStringLookup, RelatedDistinctStringLookup
from . import models


class OutcomeByDesignLookup(RelatedDistinctStringLookup):
    model = models.Outcome
    distinct_field = "endpoint"
    related_filter = "design_id"


class OutcomeByHealthOutcome(RelatedDistinctStringLookup):
    model = models.Outcome
    distinct_field = "health_outcome"
    related_filter = "design_id"

class CountryNameLookup(DistinctStringLookup):
    model = Country
    distinct_field = "name"


registry.register(OutcomeByDesignLookup)
registry.register(OutcomeByHealthOutcome)
