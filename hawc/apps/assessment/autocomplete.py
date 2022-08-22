from ..common.autocomplete import BaseAutocomplete, register
from . import models


@register
class AssessmentAutocomplete(BaseAutocomplete):
    model = models.Assessment
    search_fields = ["name"]


@register
class DSSToxAutocomplete(BaseAutocomplete):
    model = models.DSSTox
    search_fields = ["dtxsid", "content__preferredName", "content__casrn"]

    def get_result(self, obj):
        result = super().get_result(obj)
        result.update(casrn=obj.content["casrn"], chemical_name=obj.content["preferredName"])
        return result

    def get_result_label(self, result):
        return result.verbose_str


@register
class EffectTagAutocomplete(BaseAutocomplete):
    model = models.EffectTag
    search_fields = ["name"]


@register
class SpeciesAutocomplete(BaseAutocomplete):
    model = models.Species
    search_fields = ["name"]
    filter_fields = ["animalgroup__experiment__study__assessment_id"]

    @classmethod
    def get_base_queryset(cls, filters: dict = None):
        return super().get_base_queryset(filters).distinct()


@register
class StrainAutocomplete(BaseAutocomplete):
    model = models.Strain
    search_fields = ["name"]
    filter_fields = ["animalgroup__experiment__study__assessment_id"]

    @classmethod
    def get_base_queryset(cls, filters: dict = None):
        return super().get_base_queryset(filters).distinct()


@register
class ProjectTypeAutocomplete(BaseAutocomplete):
    model = models.ProjectType
    search_fields = ["name"]


@register
class SystemAutocomplete(BaseAutocomplete):
    model = models.System
    search_fields = ["name"]


@register
class DurationAutocomplete(BaseAutocomplete):
    model = models.Duration
    search_fields = ["name"]


@register
class TumorTypeAutocomplete(BaseAutocomplete):
    model = models.TumorType
    search_fields = ["name"]


@register
class ExtrapolationMethodAutocomplete(BaseAutocomplete):
    model = models.ExtrapolationMethod
    search_fields = ["name"]


@register
class EvidenceAutocomplete(BaseAutocomplete):
    model = models.EvidenceCharacterization
    search_fields = ["name"]


@register
class DoseUnitsAutocomplete(BaseAutocomplete):
    model = models.DoseUnits
    search_fields = ["name"]
