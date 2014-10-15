from selectable.base import ModelLookup
from selectable.registry import registry

from . import models


class DoseUnitsLookup(ModelLookup):
    model = models.DoseUnits


class EndpointSystemLookup(ModelLookup):
    model = models.Endpoint
    search_fields = ('system__icontains', )

    def get_item_value(self, item):
        return item.system

    def get_item_label(self, item):
        return item.system


class EndpointOrganLookup(ModelLookup):
    model = models.Endpoint
    search_fields = ('organ__icontains', )

    def get_item_value(self, item):
        return item.organ

    def get_item_label(self, item):
        return item.organ


class EndpointEffectLookup(ModelLookup):
    model = models.Endpoint
    search_fields = ('effect__icontains', )

    def get_item_value(self, item):
        return item.effect

    def get_item_label(self, item):
        return item.effect


class EndpointStatisticalTestLookup(ModelLookup):
    model = models.Endpoint
    search_fields = ('statistical_test__icontains', )

    def get_item_value(self, item):
        return item.statistical_test

    def get_item_label(self, item):
        return item.statistical_test


registry.register(DoseUnitsLookup)
registry.register(EndpointSystemLookup)
registry.register(EndpointOrganLookup)
registry.register(EndpointEffectLookup)
registry.register(EndpointStatisticalTestLookup)
