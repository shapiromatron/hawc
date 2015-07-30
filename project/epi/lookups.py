from selectable.registry import registry

from utils.lookups import DistinctStringLookup, RelatedLookup
from . import models


class StudyPopulationByStudyLookup(RelatedLookup):
    # Return names of study populations available for a particular study
    model = models.StudyPopulation
    search_fields = ('name__icontains', )
    related_filter = 'study_id'


class RegionLookup(DistinctStringLookup):
    model = models.StudyPopulation
    distinct_field = "region"


class StateLookup(DistinctStringLookup):
    model = models.StudyPopulation
    distinct_field = "state"


class StudyCriteriaLookup(RelatedLookup):
    model = models.StudyCriteria
    search_fields = ('description__icontains', )
    related_filter = 'assessment_id'


class ExposureByStudyLookup(StudyPopulationByStudyLookup):
    # Return names of exposures available for a particular study
    model = models.Exposure
    search_fields = ('exposure_form_definition__icontains', )
    related_filter = 'study_population__study_id'

    def get_item_label(self, obj):
        return u"{} | {}".format(obj.study_population, obj)

    def get_item_value(self, obj):
        return self.get_item_label(obj)


class FactorLookup(RelatedLookup):
    model = models.Factor
    search_fields = ('description__icontains', )
    related_filter = 'assessment__id'


class AssessedOutcomeByStudyLookup(StudyPopulationByStudyLookup):
    # Return names of assessed outcomes available for a particular study
    model = models.AssessedOutcome
    search_fields = (
        'name__icontains',
        'exposure__exposure_form_definition__icontains'
    )
    related_filter = 'exposure__study_population__study'

    def get_query(self, request, term):
        return super(AssessedOutcomeByStudyLookup, self)\
                .get_query(request, term).order_by('exposure')

    def get_item_label(self, obj):
        return u"{} | {} | {}".format(obj.exposure.study_population, obj.exposure, obj)

    def get_item_value(self, obj):
        return self.get_item_label(obj)


class AssessedOutcomeGroupByAOLookup(RelatedLookup):
    model = models.AssessedOutcomeGroup
    related_filter = 'assessed_outcome'


class MetaResultByStudyLookup(RelatedLookup):
    model = models.MetaResult
    search_fields = ('label__icontains', )
    related_filter = 'protocol__study'


class MetaResultHealthOutcomeLookup(DistinctStringLookup):
    model = models.MetaResult
    distinct_field = 'health_outcome'
    search_fields = ('health_outcome__icontains', )

    def get_query(self, request, term):
        try:
            id_ = int(request.GET.get('related', -1))
        except Exception:
            id_ = -1
        return self.model.objects.filter(
            protocol__study__assessment_id=id_,
            health_outcome__icontains=term)


class MetaResultExposureNameLookup(DistinctStringLookup):
    model = models.MetaResult
    distinct_field = 'exposure_name'
    search_fields = ('exposure_name__icontains', )

    def get_query(self, request, term):
        try:
            id_ = int(request.GET.get('related', -1))
        except Exception:
            id_ = -1
        return self.model.objects.filter(
            protocol__study__assessment_id=id_,
            exposure_name__icontains=term)


registry.register(StudyPopulationByStudyLookup)
registry.register(RegionLookup)
registry.register(StateLookup)
registry.register(StudyCriteriaLookup)
registry.register(ExposureByStudyLookup)
registry.register(FactorLookup)
registry.register(AssessedOutcomeByStudyLookup)
registry.register(AssessedOutcomeGroupByAOLookup)
registry.register(MetaResultByStudyLookup)
registry.register(MetaResultHealthOutcomeLookup)
registry.register(MetaResultExposureNameLookup)
