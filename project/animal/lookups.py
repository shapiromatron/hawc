from selectable.registry import registry

from . import models
from utils.lookups import DistinctStringLookup, RelatedLookup, RelatedDistinctStringLookup


class RelatedExperimentCASLookup(RelatedDistinctStringLookup):
    model = models.Experiment
    distinct_field = "cas"
    related_filter = 'study__assessment_id'


class ExperimentByStudyLookup(RelatedLookup):
    model = models.Experiment
    search_fields = ('name__icontains', )
    related_filter = 'study_id'


class AnimalGroupByExperimentLookup(RelatedLookup):
    model = models.AnimalGroup
    search_fields = ('name__icontains', )
    related_filter = 'experiment_id'


class RelatedAnimalGroupLifestageExposedLookup(RelatedDistinctStringLookup):
    model = models.AnimalGroup
    distinct_field = "lifestage_exposed"
    related_filter = 'experiment__study__assessment_id'


class RelatedAnimalGroupLifestageAssessedLookup(RelatedDistinctStringLookup):
    model = models.AnimalGroup
    distinct_field = "lifestage_assessed"
    related_filter = 'experiment__study__assessment_id'


class RelatedEndpointSystemLookup(RelatedDistinctStringLookup):
    model = models.Endpoint
    distinct_field = "system"
    related_filter = 'assessment_id'


class RelatedEndpointOrganLookup(RelatedDistinctStringLookup):
    model = models.Endpoint
    distinct_field = "organ"
    related_filter = 'assessment_id'


class RelatedEndpointEffectLookup(RelatedDistinctStringLookup):
    model = models.Endpoint
    distinct_field = "effect"
    related_filter = 'assessment_id'

	
class RelatedEndpointEffectSubtypeLookup(RelatedDistinctStringLookup):
    model = models.Endpoint
    distinct_field = "effect_subtype"
    related_filter = 'assessment_id'


class ExpChemicalLookup(DistinctStringLookup):
    model = models.Experiment
    distinct_field = "chemical"


class ExpCasLookup(DistinctStringLookup):
    model = models.Experiment
    distinct_field = "cas"


class ExpChemSourceLookup(DistinctStringLookup):
    model = models.Experiment
    distinct_field = "chemical_source"


class ExpGlpLookup(DistinctStringLookup):
    model = models.Experiment
    distinct_field = "guideline_compliance"


class EndpointSystemLookup(DistinctStringLookup):
    model = models.Endpoint
    distinct_field = "system"


class EndpointOrganLookup(DistinctStringLookup):
    model = models.Endpoint
    distinct_field = "organ"


class EndpointEffectLookup(DistinctStringLookup):
    model = models.Endpoint
    distinct_field = "effect"


class EndpointEffectSubtypeLookup(DistinctStringLookup):
    model = models.Endpoint
    distinct_field = "effect_subtype"


class EndpointStatisticalTestLookup(DistinctStringLookup):
    model = models.Endpoint
    distinct_field = "statistical_test"


class EndpointByStudyLookup(RelatedLookup):
    # Return names of endpoints available for a particular study
    model = models.Endpoint
    search_fields = (
        'name__icontains',
        'animal_group__name__icontains',
        'animal_group__experiment__name__icontains',
    )
    related_filter = 'animal_group__experiment__study'

    def get_item_label(self, obj):
        return "{} | {} | {}".format(
            obj.animal_group.experiment,
            obj.animal_group,
            obj
        )

    def get_item_value(self, obj):
        return self.get_item_label(obj)


class EndpointByAssessmentLookup(RelatedLookup):
    # Return names of endpoints available for a assessment study
    model = models.Endpoint
    search_fields = (
        'name__icontains',
        'animal_group__name__icontains',
        'animal_group__experiment__name__icontains',
        'animal_group__experiment__study__short_citation__icontains'
    )
    related_filter = 'assessment_id'

    def get_item_label(self, obj):
        return "{} | {} | {} | {}".format(
            obj.animal_group.experiment.study,
            obj.animal_group.experiment,
            obj.animal_group,
            obj
        )

    def get_item_value(self, obj):
        return self.get_item_label(obj)


class EndpointByAssessmentTextLookup(RelatedLookup):
    model = models.Endpoint
    search_fields = ('name__icontains', )
    related_filter = 'assessment_id'

    def get_query(self, request, term):
        return super().get_query(request, term)\
            .distinct('name')


class EndpointByAssessmentLookupHtml(EndpointByAssessmentLookup):

    def get_item_value(self, obj):
        return u'<a href="{}" target="_blank">{}</a>'.format(
            obj.get_absolute_url(),
            self.get_item_label(obj)
        )


registry.register(ExperimentByStudyLookup)
registry.register(AnimalGroupByExperimentLookup)
registry.register(RelatedExperimentCASLookup)
registry.register(RelatedAnimalGroupLifestageExposedLookup)
registry.register(RelatedAnimalGroupLifestageAssessedLookup)
registry.register(RelatedEndpointSystemLookup)
registry.register(RelatedEndpointOrganLookup)
registry.register(RelatedEndpointEffectLookup)
registry.register(RelatedEndpointEffectSubtypeLookup)

registry.register(ExpChemicalLookup)
registry.register(ExpCasLookup)
registry.register(ExpChemSourceLookup)
registry.register(ExpGlpLookup)
registry.register(EndpointSystemLookup)
registry.register(EndpointOrganLookup)
registry.register(EndpointEffectLookup)
registry.register(EndpointEffectSubtypeLookup)
registry.register(EndpointStatisticalTestLookup)

registry.register(EndpointByStudyLookup)
registry.register(EndpointByAssessmentLookup)
registry.register(EndpointByAssessmentTextLookup)
registry.register(EndpointByAssessmentLookupHtml)
