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


class EndpointByStudyLookup(ModelLookup):
    # Return names of endpoints available for a particular study
    model = models.Endpoint
    search_fields = ('name__icontains', 'animal_group__name__icontains')
    filter_string = 'animal_group__experiment__study'

    def get_query(self, request, term):
        try:
            pk = int(request.GET.get('related'))
        except Exception:
            return self.model.objects.none()
        filters = {self.filter_string: pk}
        return self.model.objects.filter(**filters).order_by('animal_group')

    def get_item_label(self, obj):
        return u"{} | {} | {}".format(obj.animal_group.experiment, obj.animal_group, obj)

    def get_item_value(self, obj):
        return u"{} | {} | {}".format(obj.animal_group.experiment, obj.animal_group, obj)


class EndpointByAssessmentLookup(ModelLookup):
    # Return names of endpoints available for a assessment study
    model = models.Endpoint
    search_fields = (
        'name__icontains',
        'animal_group__name__icontains',
        'animal_group__experiment__name__icontains',
        'animal_group__experiment__study__short_citation__icontains'
    )

    def get_query(self, request, term):
        try:
            pk = int(request.GET.get('assessment_id'))
            self.filters = {'assessment_id': pk}
        except Exception:
            return self.model.objects.none()
        return super(EndpointByAssessmentLookup, self).get_query(request, term)

    def get_item_label(self, obj):
        return u"{} | {} | {} | {}".format(
            obj.animal_group.experiment.study,
            obj.animal_group.experiment,
            obj.animal_group,
            obj
        )

    def get_item_value(self, obj):
        return '<a href="{}" target="_blank">{}</a>'.format(
            obj.get_absolute_url(),
            self.get_item_label(obj)
        )


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
registry.register(EndpointByStudyLookup)
registry.register(EndpointByAssessmentLookup)
