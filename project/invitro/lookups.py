from selectable.registry import registry

from . import models
from utils.lookups import RelatedDistinctStringLookup, RelatedLookup


class IVChemicalNameLookup(RelatedDistinctStringLookup):
    model = models.IVChemical
    distinct_field = 'name'
    related_filter = 'study__assessment_id'


class IVChemicalCASLookup(RelatedDistinctStringLookup):
    model = models.IVChemical
    distinct_field = 'cas'
    related_filter = 'study__assessment_id'


class IVEndpointEffectLookup(RelatedDistinctStringLookup):
    model = models.IVEndpoint
    distinct_field = 'effect'
    related_filter = 'assessment_id'


class IVEndpointResponseUnitsLookup(RelatedDistinctStringLookup):
    model = models.IVEndpoint
    distinct_field = 'response_units'
    related_filter = 'assessment_id'


class IVEndpointByAssessmentTextLookup(RelatedLookup):
    model = models.IVEndpoint
    search_fields = ('name__icontains', )
    related_filter = 'assessment_id'

    def get_query(self, request, term):
        return super(IVEndpointByAssessmentTextLookup, self)\
            .get_query(request, term)\
            .distinct('name')


class IVCellTypeNameLookup(RelatedDistinctStringLookup):
    model = models.IVCellType
    distinct_field = 'cell_type'
    related_filter = 'study__assessment_id'


class IVCellTypeTissueLookup(RelatedDistinctStringLookup):
    model = models.IVCellType
    distinct_field = 'tissue'
    related_filter = 'study__assessment_id'


registry.register(IVChemicalNameLookup)
registry.register(IVChemicalCASLookup)
registry.register(IVCellTypeNameLookup)
registry.register(IVCellTypeTissueLookup)
registry.register(IVEndpointEffectLookup)
registry.register(IVEndpointResponseUnitsLookup)
registry.register(IVEndpointByAssessmentTextLookup)
