from django.db import models


class BmdsVersion(models.TextChoices):
    BMDS2601 = "BMDS2601", "BMDS 2.6.0.1"
    BMDS270 = "BMDS270", "BMDS 2.7"
    BMDS330 = "BMDS330", "BMDS 3.3 (2022.10)"


class LogicBin(models.IntegerChoices):
    WARNING = 0, "Warning (no change)"
    QUESTIONABLE = 1, "Questionable"
    NV = 2, "Not Viable"
