from django.db import models
from pydantic import BaseModel, RootModel


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
    IMAGE = 8, "static image"


class SortOrder(models.TextChoices):
    SC = "short_citation", "Short Citation"
    OC = "overall_confidence", "Final Study Confidence"


class ExportStyle(models.IntegerChoices):
    EXPORT_GROUP = 0, "One row per Endpoint-group/Result-group"
    EXPORT_ENDPOINT = 1, "One row per Endpoint/Result"


class TableauFilter(BaseModel):
    field: str
    value: str


class TableauFilterList(RootModel):
    root: list[TableauFilter]
