from django.db import models

from ..common.constants import NO_LABEL


class CoiReported(models.IntegerChoices):
    NONE = 4, NO_LABEL
    NO_COI = 0, "Authors report they have no COI"
    COI = 1, "Authors disclosed COI"
    NR_NO_COI = (
        5,
        "Not reported; no COI is inferred based on author affiliation and/or funding source",
    )
    NR_COI = 6, "Not reported; a COI is inferred based on author affiliation and/or funding source"
    NR = 3, "Not reported"
    UNKNOWN = 2, "Unknown"


class StudyTypeChoices(models.TextChoices):
    BIOASSAY = "bioassay", "Animal bioassay"
    EPI = "epi", "Epidemiology"
    EPI_META = "epi_meta", "Epidemiology meta-analysis"
    IN_VITRO = "in_vitro", "In vitro"
    ECO = "eco", "Ecology"
