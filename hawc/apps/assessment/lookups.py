from selectable.base import ModelLookup
from selectable.registry import registry

from ..common.lookups import DistinctStringLookup
from . import models


class DoseUnitsLookup(ModelLookup):
    model = models.DoseUnits
    search_fields = ("name__icontains",)


class BaseEndpointLookup(ModelLookup):
    model = models.BaseEndpoint
    search_fields = ("name__icontains",)


class EffectTagLookup(ModelLookup):
    model = models.EffectTag
    search_fields = ("name__icontains",)


class ProjectTypeLookup(DistinctStringLookup):
    model = models.AssessmentDetails
    distinct_field = "project_type"


class DurationLookup(DistinctStringLookup):
    model = models.Values
    distinct_field = "duration"


class TumorTypeLookup(DistinctStringLookup):
    model = models.Values
    distinct_field = "tumor_type"


class ExtrapolationMethodLookup(DistinctStringLookup):
    model = models.Values
    distinct_field = "extrapolation_method"


class EvidenceLookup(DistinctStringLookup):
    model = models.Values
    distinct_field = "evidence"


registry.register(DoseUnitsLookup)
registry.register(EffectTagLookup)
registry.register(BaseEndpointLookup)
registry.register(ProjectTypeLookup)
registry.register(DurationLookup)
registry.register(TumorTypeLookup)
registry.register(ExtrapolationMethodLookup)
registry.register(EvidenceLookup)
