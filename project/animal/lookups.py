from selectable.registry import registry

from . import models
from utils.lookups import RelatedLookup, RelatedDistinctStringLookup


class ExperimentCASLookup(RelatedDistinctStringLookup):
    model = models.Experiment
    distinct_field = "cas"
    related_filter = 'study__assessment_id'


class AnimalGroupLifestageExposedLookup(RelatedDistinctStringLookup):
    model = models.AnimalGroup
    distinct_field = "lifestage_exposed"
    related_filter = 'experiment__study__assessment_id'


class AnimalGroupLifestageAssessedLookup(RelatedDistinctStringLookup):
    model = models.AnimalGroup
    distinct_field = "lifestage_assessed"
    related_filter = 'experiment__study__assessment_id'


class EndpointSystemLookup(RelatedDistinctStringLookup):
    model = models.Endpoint
    distinct_field = "system"
    related_filter = 'assessment_id'


class EndpointOrganLookup(RelatedDistinctStringLookup):
    model = models.Endpoint
    distinct_field = "organ"
    related_filter = 'assessment_id'


class EndpointEffectLookup(RelatedDistinctStringLookup):
    model = models.Endpoint
    distinct_field = "effect"
    related_filter = 'assessment_id'


class EndpointEffectSubtypeLookup(RelatedDistinctStringLookup):
    model = models.Endpoint
    distinct_field = "effect_subtype"
    related_filter = 'assessment_id'


class EndpointStatisticalTestLookup(RelatedDistinctStringLookup):
    model = models.Endpoint
    distinct_field = "statistical_test"
    related_filter = 'assessment_id'


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
        return u"{} | {} | {}".format(
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
        return u"{} | {} | {} | {}".format(
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
        return super(EndpointByAssessmentTextLookup, self)\
            .get_query(request, term)\
            .distinct('name')


class EndpointByAssessmentLookupHtml(EndpointByAssessmentLookup):

    def get_item_value(self, obj):
        return '<a href="{}" target="_blank">{}</a>'.format(
            obj.get_absolute_url(),
            self.get_item_label(obj)
        )


registry.register(ExperimentCASLookup)
registry.register(AnimalGroupLifestageExposedLookup)
registry.register(AnimalGroupLifestageAssessedLookup)
registry.register(EndpointSystemLookup)
registry.register(EndpointOrganLookup)
registry.register(EndpointEffectLookup)
registry.register(EndpointEffectSubtypeLookup)
registry.register(EndpointStatisticalTestLookup)
registry.register(EndpointByStudyLookup)
registry.register(EndpointByAssessmentLookup)
registry.register(EndpointByAssessmentTextLookup)
registry.register(EndpointByAssessmentLookupHtml)
