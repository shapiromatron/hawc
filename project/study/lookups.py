from selectable.base import ModelLookup
from selectable.registry import registry

from . import models


class StudyLookup(ModelLookup):
    model = models.Study
    search_fields = ('short_citation__icontains', )

    def get_query(self, request, term):
        results = super(StudyLookup, self).get_query(request, term)
        assessment_id = request.GET.get('assessment_id', -1)
        return results.filter(assessment_id=assessment_id)


class AnimalStudyLookup(StudyLookup):
    model = models.Study
    search_fields = ('short_citation__icontains', )

    def get_query(self, request, term):
        results = super(AnimalStudyLookup, self).get_query(request, term)
        return results.filter(study_type=0)


registry.register(StudyLookup)
registry.register(AnimalStudyLookup)
