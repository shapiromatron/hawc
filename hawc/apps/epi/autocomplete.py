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
    filter_fields = ["study_id"]


@register
class ExposureAutocomplete(BaseAutocomplete):
    model = models.Exposure
    search_fields = ["name"]
    filter_fields = ["study_population_id"]


@register
class OutcomeAutocomplete(BaseAutocomplete):
    model = models.Outcome
    search_fields = ["name"]
    filter_fields = ["study_population_id"]


@register
class ComparisonSetAutocomplete(BaseAutocomplete):
    model = models.ComparisonSet
    search_fields = ["name"]
    filter_fields = ["study_population_id", "outcome_id"]


@register
class AdjustmentFactorAutocomplete(BaseAutocomplete):
    model = models.AdjustmentFactor
    search_fields = ["description"]
    filter_fields = ["assessment_id"]


@register
class ResultAutocomplete(BaseAutocomplete):
    model = models.Result
    search_fields = ["metric__metric", "comparison_set__name"]
    filter_fields = ["outcome_id"]
