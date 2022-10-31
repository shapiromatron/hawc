from django.db import models


class BmdsVersion(models.TextChoices):
    BMDS2601 = "BMDS2601", "BMDS v2.6.0.1"
    BMDS270 = "BMDS270", "BMDS v2.7.0"
    BMDS330 = "BMDS330", "BMDS v3.3.0"


class LogicBin(models.IntegerChoices):
    WARNING = 0, "Warning (no change)"
    QUESTIONABLE = 1, "Questionable"
    NV = 2, "Not Viable"
