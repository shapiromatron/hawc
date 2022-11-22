from ..common.autocomplete import BaseAutocomplete, register
from . import models


@register
class StudyAutocomplete(BaseAutocomplete):
    model = models.Study
    search_fields = ["short_citation"]
    filter_fields = ["assessment_id", "bioassay", "epi", "epi_meta", "in_vitro", "eco"]
