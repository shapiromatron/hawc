from ..common.autocomplete import BaseAutocomplete, register
from . import models


@register
class CriteriaAutocomplete(BaseAutocomplete):
    model = models.Criteria
    search_fields = ["description"]
    filter_fields = ["assessment_id"]


@register
class StudyPopulationAutocomplete(BaseAutocomplete):
    model = models.StudyPopulation
    search_fields = ["name"]
    filter_fields = ["study_id", "study__assessment_id"]


@register
class ExposureAutocomplete(BaseAutocomplete):
    model = models.Exposure
    search_fields = ["name"]
    filter_fields = ["study_population_id", "study_population__study__assessment_id"]


@register
class OutcomeAutocomplete(BaseAutocomplete):
    model = models.Outcome
    search_fields = ["name"]
    filter_fields = ["study_population_id", "study_population__study__assessment_id"]


@register
class AdjustmentFactorAutocomplete(BaseAutocomplete):
    model = models.AdjustmentFactor
    search_fields = ["description"]
    filter_fields = ["assessment_id"]


@register
class CountryAutocomplete(BaseAutocomplete):
    model = models.Country
    search_fields = ["name"]
    filter_fields = ["studypopulation__study__assessment_id"]
