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


class EffectLookup(DistinctStringLookup):
    model = models.Outcome
    distinct_field = "effect"


class EffectDetailLookup(DistinctStringLookup):
    model = models.Outcome
    distinct_field = "effect_detail"


class ExposureLevelUnitsLookup(DistinctStringLookup):
    model = models.ExposureLevel
    distinct_field = "units"


class DataExtractionUnitsLookup(DistinctStringLookup):
    model = models.DataExtraction
    distinct_field = "units"


registry.register(CountryNameLookup)
registry.register(ChemicalNameLookup)
registry.register(EndpointLookup)
registry.register(EffectLookup)
registry.register(EffectDetailLookup)
registry.register(ExposureLevelUnitsLookup)
registry.register(DataExtractionUnitsLookup)
