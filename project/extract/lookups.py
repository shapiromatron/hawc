from selectable.base import ModelLookup
from selectable.registry import registry

from . import models
from assessment.models import Species, Strain


class SpeciesLookup(ModelLookup):
    model = models.Species
    search_fields = ('name__icontains', )


class StrainLookup(ModelLookup):
    model = models.Strain
    search_fields = ('name__icontains', )

registry.register(SpeciesLookup)
registry.register(StrainLookup)
