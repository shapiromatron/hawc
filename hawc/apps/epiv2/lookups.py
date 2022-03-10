from selectable.registry import registry

from hawc.apps.epi.models import Country

from ..common.lookups import DistinctStringLookup
from . import models


class CountryNameLookup(DistinctStringLookup):
    model = Country
    distinct_field = "name"


class ChemicalNameLookup(DistinctStringLookup):
    model = models.Chemical
    distinct_field = "name"


class EndpointLookup(DistinctStringLookup):
    model = models.Outcome
    distinct_field = "endpoint"


class HealthOutcomeLookup(DistinctStringLookup):
    model = models.Outcome
    distinct_field = "health_outcome"


class ExposureLevelUnitsLookup(DistinctStringLookup):
    model = models.ExposureLevel
    distinct_field = "units"


registry.register(CountryNameLookup)
registry.register(ChemicalNameLookup)
registry.register(EndpointLookup)
registry.register(HealthOutcomeLookup)
registry.register(ExposureLevelUnitsLookup)
