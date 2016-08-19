from selectable.registry import registry

from . import models
from utils.lookups import DistinctStringLookup, RelatedLookup


class IVChemicalNameLookup(DistinctStringLookup):
    model = models.IVChemical
    distinct_field = 'name'


class IVChemicalCASLookup(DistinctStringLookup):
    model = models.IVChemical
    distinct_field = 'cas'


class IVChemicalSourceLookup(DistinctStringLookup):
    model = models.IVChemical
    distinct_field = 'source'


class IVChemicalPurityLookup(DistinctStringLookup):
    model = models.IVChemical
    distinct_field = 'purity'


class IVEndpointEffectLookup(DistinctStringLookup):
    model = models.IVEndpoint
    distinct_field = 'effect'


class IVEndpointResponseUnitsLookup(DistinctStringLookup):
    model = models.IVEndpoint
    distinct_field = 'response_units'


class IVEndpointByAssessmentTextLookup(RelatedLookup):
    model = models.IVEndpoint
    search_fields = ('name__icontains', )
    related_filter = 'assessment_id'

    def get_query(self, request, term):
        return super(IVEndpointByAssessmentTextLookup, self)\
            .get_query(request, term)\
            .distinct('name')

registry.register(IVChemicalNameLookup)
registry.register(IVChemicalCASLookup)
registry.register(IVChemicalSourceLookup)
registry.register(IVChemicalPurityLookup)
registry.register(IVEndpointEffectLookup)
registry.register(IVEndpointResponseUnitsLookup)
registry.register(IVEndpointByAssessmentTextLookup)
