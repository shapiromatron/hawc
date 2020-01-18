from selectable.registry import registry

from utils.lookups import RelatedLookup
from . import models


class DataPivotLookup(RelatedLookup):
    model = models.DataPivot
    search_fields = ("title__icontains",)
    related_filter = "assessment_id"


class VisualLookup(RelatedLookup):
    model = models.Visual
    search_fields = ("title__icontains",)
    related_filter = "assessment_id"


registry.register(DataPivotLookup)
registry.register(VisualLookup)
