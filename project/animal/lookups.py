from selectable.base import ModelLookup
from selectable.registry import registry

from . import models
from utils.lookups import DistinctStringLookup


class SpeciesLookup(ModelLookup):
    model = models.Species
    search_fields = ('name__icontains', )


class StrainLookup(ModelLookup):
    model = models.Strain
    search_fields = ('name__icontains', )


class ExperimentCASLookup(DistinctStringLookup):
    model = models.Experiment
    distinct_field = "cas"


class AnimalGroupLifestageExposedLookup(DistinctStringLookup):
    model = models.AnimalGroup
    distinct_field = "lifestage_exposed"


class AnimalGroupLifestageAssessedLookup(DistinctStringLookup):
    model = models.AnimalGroup
    distinct_field = "lifestage_assessed"


class DoseUnitsLookup(ModelLookup):
    model = models.DoseUnits


class EndpointSystemLookup(DistinctStringLookup):
    model = models.Endpoint
    distinct_field = "system"


class EndpointOrganLookup(DistinctStringLookup):
    model = models.Endpoint
    distinct_field = "organ"


class EndpointEffectLookup(DistinctStringLookup):
    model = models.Endpoint
    distinct_field = "effect"


class EndpointStatisticalTestLookup(DistinctStringLookup):
    model = models.Endpoint
    distinct_field = "statistical_test"


registry.register(SpeciesLookup)
registry.register(StrainLookup)
registry.register(ExperimentCASLookup)
registry.register(AnimalGroupLifestageExposedLookup)
registry.register(AnimalGroupLifestageAssessedLookup)
registry.register(DoseUnitsLookup)
registry.register(EndpointSystemLookup)
registry.register(EndpointOrganLookup)
registry.register(EndpointEffectLookup)
registry.register(EndpointStatisticalTestLookup)
