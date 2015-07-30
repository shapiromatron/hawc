from selectable.registry import registry

from utils.lookups import RelatedLookup
from . import models


class StudyLookup(RelatedLookup):
    model = models.Study
    search_fields = ('short_citation__icontains', )
    related_filter = "assessment_id"


class AnimalStudyLookup(StudyLookup):
    model = models.Study
    search_fields = ('short_citation__icontains', )
    filters = {"study_type": 0}


registry.register(StudyLookup)
registry.register(AnimalStudyLookup)
