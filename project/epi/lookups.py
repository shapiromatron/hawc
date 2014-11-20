from selectable.base import ModelLookup
from selectable.registry import registry

from . import models


class StudyPopulationByStudyLookup(ModelLookup):
    # Return names of study populations available for a particular study
    model = models.StudyPopulation
    search_fields = ('name__icontains')
    filter_string = 'study'

    def get_query(self, request, term):
        try:
            pk = int(request.GET.get('related'))
        except Exception:
            return self.model.objects.none()
        filters = {self.filter_string: pk}
        return self.model.objects.filter(**filters)


class RegionLookup(ModelLookup):
    model = models.StudyPopulation
    search_fields = ('region__icontains', )

    def get_item_value(self, item):
        return item.region

    def get_item_label(self, item):
        return item.region


class StateLookup(ModelLookup):
    model = models.StudyPopulation
    search_fields = ('state__icontains', )

    def get_item_value(self, item):
        return item.state

    def get_item_label(self, item):
        return item.state


class StudyCriteriaLookup(ModelLookup):
    model = models.StudyCriteria
    search_fields = ('description__icontains', )

    def get_query(self, request, term):
        results = super(StudyCriteriaLookup, self).get_query(request, term)
        assessment = request.GET.get('assessment', -1)  # return none if no assessment specified
        results = results.filter(assessment=assessment)
        return results


class ExposureByStudyLookup(StudyPopulationByStudyLookup):
    # Return names of exposures available for a particular study
    model = models.Exposure
    search_fields = ('exposure_form_definition__icontains')
    filter_string = 'study_population__study'

    def get_item_label(self, obj):
        return u"{} | {}".format(obj.study_population, obj)

    def get_item_value(self, obj):
        return u"{} | {}".format(obj.study_population, obj)


class FactorLookup(ModelLookup):
    model = models.Factor
    search_fields = ('description__icontains', )

    def get_query(self, request, term):
        results = super(FactorLookup, self).get_query(request, term)
        assessment = request.GET.get('assessment', -1)  # return none if no assessment specified
        results = results.filter(assessment=assessment)
        return results


class AssessedOutcomeByStudyLookup(StudyPopulationByStudyLookup):
    # Return names of assessed outcomes available for a particular study
    model = models.AssessedOutcome
    search_fields = ('name__icontains', 'exposure__exposure_form_definition__icontains')
    filter_string = 'exposure__study_population__study'

    def get_query(self, request, term):
        qs = super(AssessedOutcomeByStudyLookup, self).get_query(request, term)
        return qs.order_by('exposure')

    def get_item_label(self, obj):
        return u"{} | {} | {}".format(obj.exposure.study_population, obj.exposure, obj)

    def get_item_value(self, obj):
        return u"{} | {} | {}".format(obj.exposure.study_population, obj.exposure, obj)


class AssessedOutcomeGroupByAOLookup(ModelLookup):
    model = models.AssessedOutcomeGroup

    def get_query(self, request, term):
        try:
            ao_pk = int(request.GET.get('related'))
        except Exception:
            return self.model.objects.none()
        return self.model.objects.filter(assessed_outcome=ao_pk)


class MetaResultByStudyLookup(ModelLookup):
    # Return names of meta-results available for a particular study
    model = models.MetaResult
    search_fields = ('label__icontains', )

    def get_query(self, request, term):
        try:
            study_pk = int(request.GET.get('related'))
        except Exception:
            return self.model.objects.none()
        return self.model.objects.filter(protocol__study=study_pk)


class MetaResultHealthOutcomeLookup(ModelLookup):
    model = models.MetaResult
    search_fields = ('health_outcome__icontains', )

    def get_query(self, request, term):
        try:
            pk = int(request.GET.get('assessment'))
        except Exception:
            return self.model.objects.none()
        return self.model.objects.filter(protocol__study__assessment_id=pk)

    def get_item_value(self, item):
        return item.health_outcome

    def get_item_label(self, item):
        return item.health_outcome


class MetaResultExposureNameLookup(ModelLookup):
    model = models.MetaResult
    search_fields = ('exposure_name__icontains', )

    def get_query(self, request, term):
        try:
            pk = int(request.GET.get('assessment'))
        except Exception:
            return self.model.objects.none()
        return self.model.objects.filter(protocol__study__assessment_id=pk)

    def get_item_value(self, item):
        return item.exposure_name

    def get_item_label(self, item):
        return item.exposure_name


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
