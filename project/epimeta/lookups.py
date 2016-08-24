from selectable.registry import registry

from utils.lookups import DistinctStringLookup, RelatedLookup
from utils.helper import tryParseInt
from . import models


class MetaResultByStudyLookup(RelatedLookup):
    model = models.MetaResult
    search_fields = ('label__icontains', )
    related_filter = 'protocol__study'


class MetaResultByAssessmentLookup(RelatedLookup):
    model = models.MetaResult
    search_fields = ('label__icontains', )
    related_filter = 'protocol__study__assessment_id'


class MetaResultHealthOutcomeLookup(DistinctStringLookup):
    model = models.MetaResult
    distinct_field = 'health_outcome'
    search_fields = ('health_outcome__icontains', )


class MetaResultExposureNameLookup(DistinctStringLookup):
    model = models.MetaResult
    distinct_field = 'exposure_name'
    search_fields = ('exposure_name__icontains', )


class MetaProtocolLookup(RelatedLookup):
    model = models.MetaProtocol
    search_fields = ('name__icontains', )
    related_filter = 'study__assessment_id'


class ExposureLookup(DistinctStringLookup):
    model = models.MetaResult
    distinct_field = 'exposure_name'
    search_fields = ('exposure_name__icontains', )


class NumberStudiesLookup(DistinctStringLookup):
    model = models.MetaResult
    distinct_field = 'number_studies'
    search_fields = ('number_studies__icontains', )


registry.register(MetaResultByStudyLookup)
registry.register(MetaResultByAssessmentLookup)
registry.register(MetaResultHealthOutcomeLookup)
registry.register(MetaResultExposureNameLookup)
registry.register(MetaProtocolLookup)
registry.register(ExposureLookup)
