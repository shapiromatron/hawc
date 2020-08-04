from django.db.models import QuerySet
from selectable.base import ModelLookup
from selectable.registry import registry

from ..common.helper import tryParseInt
from . import models


class EhvTermLookup(ModelLookup):
    model = models.Term
    search_fields = ("name__icontains",)
    filters = dict(namespace=models.VocabularyNamespace.EHV, deprecated_on__isnull=True,)
    term_type: models.VocabularyTermType

    def get_query(self, request, term) -> QuerySet:
        qs = super().get_query(request, term).filter(type=self.term_type)
        id_ = tryParseInt(request.GET.get("parent"), None)
        if id_:
            qs = qs.filter(parents=id_)
        return qs.order_by("name").distinct("name")

    def get_item_value(self, item) -> str:
        return item.name

    def get_item_label(self, item) -> str:
        return item.name


class SystemLookup(EhvTermLookup):
    term_type = models.VocabularyTermType.system


class OrganLookup(EhvTermLookup):
    term_type = models.VocabularyTermType.organ


class EffectLookup(EhvTermLookup):
    term_type = models.VocabularyTermType.effect


class EffectSubtypeLookup(EhvTermLookup):
    term_type = models.VocabularyTermType.effect_subtype


class EndpointNameLookup(EhvTermLookup):
    term_type: models.VocabularyTermType = models.VocabularyTermType.endpoint_name


registry.register(SystemLookup)
registry.register(OrganLookup)
registry.register(EffectLookup)
registry.register(EffectSubtypeLookup)
registry.register(EndpointNameLookup)
