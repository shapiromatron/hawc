from selectable.registry import registry

from . import models
from utils.lookups import (
    DistinctStringLookup,
    RelatedDistinctStringLookup,
    RelatedLookup,
)


# Chemical
class RelatedIVChemicalNameLookup(RelatedDistinctStringLookup):
    model = models.IVChemical
    distinct_field = "name"
    related_filter = "study__assessment_id"


class RelatedIVChemicalCASLookup(RelatedDistinctStringLookup):
    model = models.IVChemical
    distinct_field = "cas"
    related_filter = "study__assessment_id"


class IVChemicalSourceLookup(DistinctStringLookup):
    model = models.IVChemical
    distinct_field = "source"


class IVChemicalPurityLookup(DistinctStringLookup):
    model = models.IVChemical
    distinct_field = "purity"


# CellType
class RelatedIVCellTypeNameLookup(RelatedDistinctStringLookup):
    model = models.IVCellType
    distinct_field = "cell_type"
    related_filter = "study__assessment_id"


class IVCellTypeSpeciesLookup(DistinctStringLookup):
    model = models.IVCellType
    distinct_field = "species"


class IVCellTypeStrainLookup(DistinctStringLookup):
    model = models.IVCellType
    distinct_field = "strain"


class IVCellTypeCellTypeLookup(DistinctStringLookup):
    model = models.IVCellType
    distinct_field = "cell_type"


class RelatedIVCellTypeTissueLookup(RelatedDistinctStringLookup):
    model = models.IVCellType
    distinct_field = "tissue"
    related_filter = "study__assessment_id"


class IVCellTypeTissueLookup(DistinctStringLookup):
    model = models.IVCellType
    distinct_field = "tissue"


class IVCellTypeSourceLookup(DistinctStringLookup):
    model = models.IVCellType
    distinct_field = "source"


# Experiment
class IVExperimentTransfectionLookup(DistinctStringLookup):
    model = models.IVExperiment
    distinct_field = "transfection"


class IVExperimentPositiveControlLookup(DistinctStringLookup):
    model = models.IVExperiment
    distinct_field = "positive_control"


class IVExperimentNegativeControlLookup(DistinctStringLookup):
    model = models.IVExperiment
    distinct_field = "negative_control"


class IVExperimentVehicleControlLookup(DistinctStringLookup):
    model = models.IVExperiment
    distinct_field = "vehicle_control"


# Endpoint
class RelatedIVEndpointEffectLookup(RelatedDistinctStringLookup):
    model = models.IVEndpoint
    distinct_field = "effect"
    related_filter = "assessment_id"


class IVEndpointEffectLookup(DistinctStringLookup):
    model = models.IVEndpoint
    distinct_field = "effect"


class IVEndpointAssayTypeLookup(DistinctStringLookup):
    model = models.IVEndpoint
    distinct_field = "assay_type"


class IVEndpointResponseUnitsLookup(DistinctStringLookup):
    model = models.IVEndpoint
    distinct_field = "response_units"


class RelatedIVEndpointResponseUnitsLookup(RelatedDistinctStringLookup):
    model = models.IVEndpoint
    distinct_field = "response_units"
    related_filter = "assessment_id"


class IVEndpointByAssessmentTextLookup(RelatedLookup):
    model = models.IVEndpoint
    search_fields = ("name__icontains",)
    related_filter = "assessment_id"

    def get_query(self, request, term):
        return super().get_query(request, term).distinct("name")


# Chemical
registry.register(RelatedIVChemicalNameLookup)
registry.register(RelatedIVChemicalCASLookup)
registry.register(IVChemicalSourceLookup)
registry.register(IVChemicalPurityLookup)

# CellType
registry.register(RelatedIVCellTypeNameLookup)
registry.register(IVCellTypeSpeciesLookup)
registry.register(IVCellTypeStrainLookup)
registry.register(IVCellTypeCellTypeLookup)
registry.register(RelatedIVCellTypeTissueLookup)
registry.register(IVCellTypeTissueLookup)
registry.register(IVCellTypeSourceLookup)

# Experiment
registry.register(IVExperimentTransfectionLookup)
registry.register(IVExperimentPositiveControlLookup)
registry.register(IVExperimentNegativeControlLookup)
registry.register(IVExperimentVehicleControlLookup)

# Endpoint
registry.register(RelatedIVEndpointEffectLookup)
registry.register(IVEndpointEffectLookup)
registry.register(IVEndpointAssayTypeLookup)
registry.register(IVEndpointResponseUnitsLookup)
registry.register(RelatedIVEndpointResponseUnitsLookup)
registry.register(IVEndpointByAssessmentTextLookup)
