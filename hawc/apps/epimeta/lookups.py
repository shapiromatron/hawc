from selectable.registry import registry

from ..common.lookups import RelatedDistinctStringLookup, RelatedLookup
from . import models


class MetaResultByAssessmentLookup(RelatedLookup):
    model = models.MetaResult
    search_fields = ("label__icontains",)
    related_filter = "protocol__study__assessment_id"


class MetaResultHealthOutcomeLookup(RelatedDistinctStringLookup):
    model = models.MetaResult
    distinct_field = "health_outcome"
    search_fields = ("health_outcome__icontains",)
    related_filter = "protocol__study__assessment_id"


class MetaResultExposureNameLookup(RelatedDistinctStringLookup):
    model = models.MetaResult
    distinct_field = "exposure_name"
    search_fields = ("exposure_name__icontains",)
    related_filter = "protocol__study__assessment_id"


class MetaProtocolLookup(RelatedLookup):
    model = models.MetaProtocol
    search_fields = ("name__icontains",)
    related_filter = "study__assessment_id"


class ExposureLookup(RelatedDistinctStringLookup):
    model = models.MetaResult
    distinct_field = "exposure_name"
    search_fields = ("exposure_name__icontains",)
    related_filter = "protocol__study__assessment_id"


registry.register(MetaResultByAssessmentLookup)
registry.register(MetaResultHealthOutcomeLookup)
registry.register(MetaResultExposureNameLookup)
registry.register(MetaProtocolLookup)
registry.register(ExposureLookup)
