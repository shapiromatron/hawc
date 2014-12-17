from selectable.base import ModelLookup
from selectable.registry import registry

from . import models


class DistinctStringLookup(ModelLookup):
    distinct_field = None

    def get_query(self, request, term):
        qs = super(DistinctStringLookup, self).get_query(request, term)
        return qs.distinct(self.distinct_field)


class DoseUnitsLookup(ModelLookup):
    model = models.DoseUnits


class EndpointSystemLookup(DistinctStringLookup):
    model = models.Endpoint
    search_fields = ("system__icontains", )
    distinct_field = "system"

    def get_item_value(self, item):
        return item.system

    def get_item_label(self, item):
        return item.system


class EndpointOrganLookup(DistinctStringLookup):
    model = models.Endpoint
    search_fields = ("organ__icontains", )
    distinct_field = "organ"

    def get_item_value(self, item):
        return item.organ

    def get_item_label(self, item):
        return item.organ


class EndpointEffectLookup(DistinctStringLookup):
    model = models.Endpoint
    search_fields = ("effect__icontains", )
    distinct_field = "effect"

    def get_item_value(self, item):
        return item.effect

    def get_item_label(self, item):
        return item.effect


class EndpointStatisticalTestLookup(ModelLookup):
    model = models.Endpoint
    search_fields = ("statistical_test__icontains", )

    def get_item_value(self, item):
        return item.statistical_test

    def get_item_label(self, item):
        return item.statistical_test


registry.register(DoseUnitsLookup)
registry.register(EndpointSystemLookup)
registry.register(EndpointOrganLookup)
registry.register(EndpointEffectLookup)
registry.register(EndpointStatisticalTestLookup)
