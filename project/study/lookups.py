from selectable.registry import registry

from utils.lookups import RelatedLookup
from . import models


class StudyLookup(RelatedLookup):
    model = models.Study
    search_fields = ("short_citation__icontains",)
    related_filter = "assessment_id"


class AnimalStudyLookup(StudyLookup):
    filters = {
        "bioassay": True,
    }


class EpiStudyLookup(StudyLookup):
    filters = {
        "epi": True,
    }


class EpimetaStudyLookup(StudyLookup):
    filters = {
        "epi_meta": True,
    }


class InvitroStudyLookup(StudyLookup):
    filters = {
        "in_vitro": True,
    }


registry.register(StudyLookup)
registry.register(AnimalStudyLookup)
registry.register(EpiStudyLookup)
registry.register(EpimetaStudyLookup)
registry.register(InvitroStudyLookup)
