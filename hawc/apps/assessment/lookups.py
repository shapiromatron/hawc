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


registry.register(DoseUnitsLookup)
registry.register(EffectTagLookup)
registry.register(BaseEndpointLookup)
