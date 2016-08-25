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


class IVChemicalSourceLookup(RelatedDistinctStringLookup):
    model = models.IVChemical
    distinct_field = 'source'
    related_filter = 'study__assessment_id'


class IVChemicalPurityLookup(RelatedDistinctStringLookup):
    model = models.IVChemical
    distinct_field = 'purity'
    related_filter = 'study__assessment_id'


class IVCellTypeSpeciesLookup(RelatedDistinctStringLookup):
    model = models.IVCellType
    distinct_field = 'species'
    related_filter = 'study__assessment_id'


class IVCellTypeStrainLookup(RelatedDistinctStringLookup):
    model = models.IVCellType
    distinct_field = 'strain'
    related_filter = 'study__assessment_id'


class IVCellTypeCellTypeLookup(RelatedDistinctStringLookup):
    model = models.IVCellType
    distinct_field = 'cell_type'
    related_filter = 'study__assessment_id'


class IVCellTypeTissueLookup(RelatedDistinctStringLookup):
    model = models.IVCellType
    distinct_field = 'tissue'
    related_filter = 'study__assessment_id'


class IVCellTypeSourceLookup(RelatedDistinctStringLookup):
    model = models.IVCellType
    distinct_field = 'source'
    related_filter = 'study__assessment_id'


class IVExperimentTransfectionLookup(RelatedDistinctStringLookup):
    model = models.IVExperiment
    distinct_field = 'transfection'
    related_filter = 'study__assessment_id'


class IVExperimentPositiveControlLookup(RelatedDistinctStringLookup):
    model = models.IVExperiment
    distinct_field = 'positive_control'
    related_filter = 'study__assessment_id'


class IVExperimentNegativeControlLookup(RelatedDistinctStringLookup):
    model = models.IVExperiment
    distinct_field = 'negative_control'
    related_filter = 'study__assessment_id'


class IVExperimentVehicleControlLookup(RelatedDistinctStringLookup):
    model = models.IVExperiment
    distinct_field = 'vehicle_control'
    related_filter = 'study__assessment_id'


class IVEndpointEffectLookup(RelatedDistinctStringLookup):
    model = models.IVEndpoint
    distinct_field = 'effect'
    related_filter = 'assessment_id'


class IVEndpointAssayTypeLookup(RelatedDistinctStringLookup):
    model = models.IVEndpoint
    distinct_field = 'assay_type'
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

registry.register(IVChemicalNameLookup)
registry.register(IVChemicalCASLookup)
registry.register(IVChemicalSourceLookup)
registry.register(IVChemicalPurityLookup)
registry.register(IVCellTypeSpeciesLookup)
registry.register(IVCellTypeStrainLookup)
registry.register(IVCellTypeCellTypeLookup)
registry.register(IVCellTypeTissueLookup)
registry.register(IVCellTypeSourceLookup)
registry.register(IVExperimentTransfectionLookup)
registry.register(IVExperimentPositiveControlLookup)
registry.register(IVExperimentNegativeControlLookup)
registry.register(IVExperimentVehicleControlLookup)
registry.register(IVEndpointEffectLookup)
registry.register(IVEndpointAssayTypeLookup)
registry.register(IVEndpointResponseUnitsLookup)
registry.register(IVEndpointByAssessmentTextLookup)
