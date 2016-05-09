from selectable.registry import registry

from utils.lookups import DistinctStringLookup, RelatedLookup
from utils.helper import tryParseInt
from . import models


class MetaResultByStudyLookup(RelatedLookup):
    model = models.MetaResult
    search_fields = ('label__icontains', )
    related_filter = 'protocol__study'


class MetaResultHealthOutcomeLookup(DistinctStringLookup):
    model = models.MetaResult
    distinct_field = 'health_outcome'
    search_fields = ('health_outcome__icontains', )

    def get_query(self, request, term):
        id_ = tryParseInt(request.GET.get('related'), -1)
        return self.model.objects.filter(
            protocol__study__assessment_id=id_,
            health_outcome__icontains=term)


class MetaResultExposureNameLookup(DistinctStringLookup):
    model = models.MetaResult
    distinct_field = 'exposure_name'
    search_fields = ('exposure_name__icontains', )

    def get_query(self, request, term):
        id_ = tryParseInt(request.GET.get('related'), -1)
        return self.model.objects.filter(
            protocol__study__assessment_id=id_,
            exposure_name__icontains=term)


registry.register(MetaResultByStudyLookup)
registry.register(MetaResultHealthOutcomeLookup)
registry.register(MetaResultExposureNameLookup)
