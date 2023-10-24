from django.db import models
from pydantic import BaseModel


class StudyType(models.IntegerChoices):
    BIOASSAY = 0, "Animal Bioassay"
    EPI = 1, "Epidemiology"
    EPI_META = 4, "Epidemiology meta-analysis/pooled analysis"
    IN_VITRO = 2, "In vitro"
    ECO = 5, "Ecology"
    OTHER = 3, "Other"


class TableType(models.IntegerChoices):
    GENERIC = 0
    EVIDENCE_PROFILE = 1
    STUDY_EVALUATION = 2


class VisualType(models.IntegerChoices):
    BIOASSAY_AGGREGATION = 0, "animal bioassay endpoint aggregation"
    BIOASSAY_CROSSVIEW = 1, "animal bioassay endpoint crossview"
    ROB_HEATMAP = 2, "risk of bias heatmap"
    ROB_BARCHART = 3, "risk of bias barchart"
    LITERATURE_TAGTREE = 4, "literature tagtree"
    EXTERNAL_SITE = 5, "embedded external website"
    EXPLORE_HEATMAP = 6, "exploratory heatmap"
    PLOTLY = 7, "plotly"


VISUAL_EVIDENCE_CHOICES = {
    VisualType.BIOASSAY_AGGREGATION: {StudyType.BIOASSAY},
    VisualType.BIOASSAY_CROSSVIEW: {StudyType.BIOASSAY},
    VisualType.ROB_HEATMAP: {StudyType.BIOASSAY, StudyType.EPI, StudyType.IN_VITRO},
    VisualType.ROB_BARCHART: {StudyType.BIOASSAY, StudyType.EPI},
    VisualType.LITERATURE_TAGTREE: {StudyType.OTHER},
    VisualType.EXTERNAL_SITE: {StudyType.OTHER},
    VisualType.EXPLORE_HEATMAP: {StudyType.OTHER},
    VisualType.PLOTLY: {StudyType.OTHER},
}


def get_default_evidence_type(visual_type: VisualType):
    choices = VISUAL_EVIDENCE_CHOICES[visual_type]
    if len(choices) > 1:
        raise ValueError(
            f"No default evidence type for visual {visual_type}; choices are {', '.join([str(_) for _ in choices])}."
        )
    return next(iter(choices))


class SortOrder(models.TextChoices):
    SC = "short_citation", "Short Citation"
    OC = "overall_confidence", "Final Study Confidence"


class ExportStyle(models.IntegerChoices):
    EXPORT_GROUP = 0, "One row per Endpoint-group/Result-group"
    EXPORT_ENDPOINT = 1, "One row per Endpoint/Result"


class TableauFilter(BaseModel):
    field: str
    value: str


class TableauFilterList(BaseModel):
    __root__: list[TableauFilter]
