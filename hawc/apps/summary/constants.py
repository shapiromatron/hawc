from django.db import models
from pydantic import BaseModel, RootModel


class StudyType(models.IntegerChoices):
    BIOASSAY = 0, "Animal Bioassay"
    EPI = 1, "Epidemiology"
    EPI_META = 4, "Epidemiology meta-analysis/pooled analysis"
    IN_VITRO = 2, "In vitro"
    ECO = 5, "Ecology"
    OTHER = 3, "Other"

    def study_filter_prefix(self):
        mapping = {
            0: "bioassay",
            1: "epi",
            4: "epi_meta",
            2: "in_vitro",
            5: "eco",
        }
        try:
            return mapping[self]
        except KeyError:
            raise ValueError(f"No study_filter_prefix for {self}") from None

    def rob_prefix(self):
        mapping = {
            0: "required_animal",
            1: "required_epi",
            2: "required_invitro",
        }
        try:
            return mapping[self]
        except KeyError:
            raise ValueError(f"No rob_prefix for {self}") from None


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
    PRISMA = 9, "PRISMA"
    DATA_PIVOT_QUERY = 10, "Data Pivot Query"
    DATA_PIVOT_FILE = 11, "Data Pivot File"


VISUAL_EVIDENCE_CHOICES = {
    VisualType.BIOASSAY_AGGREGATION: {StudyType.BIOASSAY},
    VisualType.BIOASSAY_CROSSVIEW: {StudyType.BIOASSAY},
    VisualType.DATA_PIVOT_QUERY: {
        StudyType.BIOASSAY,
        StudyType.EPI,
        StudyType.EPI_META,
        StudyType.IN_VITRO,
        StudyType.ECO,
    },
    VisualType.DATA_PIVOT_FILE: {StudyType.OTHER},
    VisualType.ROB_HEATMAP: {StudyType.BIOASSAY, StudyType.EPI, StudyType.IN_VITRO},
    VisualType.ROB_BARCHART: {StudyType.BIOASSAY, StudyType.EPI, StudyType.IN_VITRO},
    VisualType.LITERATURE_TAGTREE: {StudyType.OTHER},
    VisualType.EXTERNAL_SITE: {StudyType.OTHER},
    VisualType.EXPLORE_HEATMAP: {StudyType.OTHER},
    VisualType.PLOTLY: {StudyType.OTHER},
    VisualType.IMAGE: {StudyType.OTHER},
    VisualType.PRISMA: {StudyType.OTHER},
}


def get_default_evidence_type(visual_type: VisualType) -> StudyType:
    """Return StudyType for visual if only one option exists, otherwise raise ValueError."""
    choices = VISUAL_EVIDENCE_CHOICES[visual_type]
    if len(choices) > 1:
        raise ValueError(f"No default evidence type for visual {visual_type}; multiple exist.")
    return next(iter(choices))


class ExportStyle(models.IntegerChoices):
    EXPORT_GROUP = 0, "One row per Endpoint-group/Result-group"
    EXPORT_ENDPOINT = 1, "One row per Endpoint/Result"


class TableauFilter(BaseModel):
    field: str
    value: str


class TableauFilterList(RootModel):
    root: list[TableauFilter]
