from selectable.base import ModelLookup
from selectable.registry import registry

from ..common.lookups import RelatedDistinctStringLookup
from ..epi.models import Country
from . import constants, models


class RelatedCauseLookup(RelatedDistinctStringLookup):
    model = models.Cause
    distinct_field = "name"
    related_filter = "study__assessment_id"

    def get_item_label(self, item):
        return f"{item.term.name} | {item.name}"

    def get_item_value(self, item):
        return f"{item.term.name} | {item.name}"


class RelatedEffectLookup(RelatedDistinctStringLookup):
    model = models.Effect
    distinct_field = "name"
    related_filter = "study__assessment_id"

    def get_item_label(self, obj):
        return f"{obj.term.name} | {obj.name}"

    def get_item_value(self, obj):
        return f"{obj.term.name} | {obj.name}"


class CountryLookup(ModelLookup):
    model = Country
    search_fields = ("code__iexact", "name__icontains")


class StateLookup(ModelLookup):
    model = models.State
    search_fields = ("code__iexact", "name__icontains")


class EcoregionLookup(ModelLookup):
    model = models.Vocab
    search_fields = ("value__icontains",)

    def get_queryset(self):
        return super().get_queryset().filter(category=constants.VocabCategories.ECOREGION)


class NestedTermLookup(ModelLookup):
    model = models.NestedTerm
    search_fields = ("name__icontains",)

    def get_item_label(self, obj):
        path = ""
        for node in obj.get_ancestors():
            path += f"{node.name} > "
        path += f"{obj.name}"
        return path

    def get_item_value(self, obj):
        path = ""
        for node in obj.get_ancestors():
            path += f"{node.name} > "
        path += f"{obj.name}"
        return path


registry.register(RelatedCauseLookup)
registry.register(RelatedEffectLookup)
registry.register(CountryLookup)
registry.register(StateLookup)
registry.register(EcoregionLookup)
registry.register(NestedTermLookup)
