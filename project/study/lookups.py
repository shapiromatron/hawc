from selectable.base import ModelLookup
from selectable.registry import registry

from . import models


class StudyLookup(ModelLookup):
    model = models.Study
    search_fields = ('short_citation__icontains', )

    def get_query(self, request, term):
        results = super(StudyLookup, self).get_query(request, term)
        assessment = request.GET.get('assessment', -1)  # return none if no assessment specified
        print assessment
        return results.filter(assessment=assessment)


class AnimalStudyLookup(StudyLookup):
    model = models.Study
    search_fields = ('short_citation__icontains', )

    def get_query(self, request, term):
        results = super(AnimalStudyLookup, self).get_query(request, term)
        return results.filter(study_type=0)


registry.register(StudyLookup)
registry.register(AnimalStudyLookup)
