from selectable.base import ModelLookup
from selectable.registry import registry

from ..common.lookups import RelatedDistinctStringLookup
from ..epi.models import Country
from . import constants, models


class RelatedCauseLookup(RelatedDistinctStringLookup):
    model = models.Cause
    distinct_field = "name"
    related_filter = "study__assessment_id"


class RelatedEffectLookup(RelatedDistinctStringLookup):
    model = models.Effect
    distinct_field = "name"
    related_filter = "study__assessment_id"


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


registry.register(RelatedCauseLookup)
registry.register(RelatedEffectLookup)
registry.register(CountryLookup)
registry.register(StateLookup)
registry.register(EcoregionLookup)
