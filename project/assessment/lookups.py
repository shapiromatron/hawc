from selectable.base import ModelLookup
from selectable.registry import registry

from . import models


class BaseEndpointLookup(ModelLookup):
    model = models.BaseEndpoint
    search_fields = ('name__icontains', )


class EffectTagLookup(ModelLookup):
    model = models.EffectTag
    search_fields = ('name__icontains', )


registry.register(BaseEndpointLookup)
registry.register(EffectTagLookup)
