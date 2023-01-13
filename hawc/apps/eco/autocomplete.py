from ..common.autocomplete import BaseAutocomplete, register
from . import constants, models


@register
class CauseAutocomplete(BaseAutocomplete):
    model = models.Cause
    filter_fields = ["study__assessment_id"]


@register
class EffectAutocomplete(BaseAutocomplete):
    model = models.Effect
    filter_fields = ["study__assessment_id"]


@register
class StateAutocomplete(BaseAutocomplete):
    model = models.State
    search_fields = ["code", "name"]


@register
class EcoregionAutocomplete(BaseAutocomplete):
    model = models.Vocab
    search_fields = ["value"]

    def get_queryset(self):
        return super().get_queryset().filter(category=constants.VocabCategories.ECOREGION)


@register
class NestedTermAutocomplete(BaseAutocomplete):
    model = models.NestedTerm
    search_fields = ("id", "name")

    def get_result_label(self, obj):
        return f"{obj.label()} ({obj.id})"
