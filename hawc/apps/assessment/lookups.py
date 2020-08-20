from selectable.base import ModelLookup
from selectable.registry import registry

from . import models


class DssToxIdLookup(ModelLookup):
    model = models.DSSTox
    search_fields = (
        "dtxsid__icontains",
        "content__preferredName__icontains",
        "content__casrn__icontains",
    )

    def get_item_label(self, obj):
        return obj.verbose_str

    def format_item(self, item):
        result = super().format_item(item)
        result.update(casrn=item.content["casrn"], chemical_name=item.content["preferredName"])
        return result


class AssessmentLookup(ModelLookup):
    model = models.Assessment
    search_fields = ("name__icontains",)


class SpeciesLookup(ModelLookup):
    model = models.Species
    search_fields = ("name__icontains",)


class StrainLookup(ModelLookup):
    model = models.Strain
    search_fields = ("name__icontains",)


class DoseUnitsLookup(ModelLookup):
    model = models.DoseUnits
    search_fields = ("name__icontains",)


class BaseEndpointLookup(ModelLookup):
    model = models.BaseEndpoint
    search_fields = ("name__icontains",)


class EffectTagLookup(ModelLookup):
    model = models.EffectTag
    search_fields = ("name__icontains",)


registry.register(DssToxIdLookup)
registry.register(AssessmentLookup)
registry.register(SpeciesLookup)
registry.register(DoseUnitsLookup)
registry.register(StrainLookup)
registry.register(EffectTagLookup)
registry.register(BaseEndpointLookup)
