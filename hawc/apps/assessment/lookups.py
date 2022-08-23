from selectable.base import ModelLookup
from selectable.registry import registry

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


class ProjectTypeLookup(ModelLookup):
    model = models.AssessmentDetails
    search_fields = ("project_type__icontains",)


class DurationLookup(ModelLookup):
    model = models.Values
    search_fields = ("duration__icontains",)


class TumorTypeLookup(ModelLookup):
    model = models.Values
    search_fields = ("tumor_type__icontains",)


class ExtrapolationMethodLookup(ModelLookup):
    model = models.Values
    search_fields = ("extrapolation_method__icontains",)


class EvidenceLookup(ModelLookup):
    model = models.Values
    search_fields = ("evidence__icontains",)


registry.register(DoseUnitsLookup)
registry.register(EffectTagLookup)
registry.register(BaseEndpointLookup)
