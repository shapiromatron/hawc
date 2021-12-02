from django.db import models


class NoelName(models.IntegerChoices):
    NOEL = 0, "NOEL/LOEL"
    NOAEL = 1, "NOAEL/LOAEL"
    NEL = 2, "NEL/LEL"


class RobName(models.IntegerChoices):
    ROB = 0, "Risk of bias"
    SE = 1, "Study evaluation"


class JobStatus(models.IntegerChoices):
    PENDING = 0, "PENDING"
    SUCCESS = 2, "SUCCESS"
    FAILURE = 3, "FAILURE"


class JobType(models.IntegerChoices):
    TEST = 1, "TEST"


### STOP HHHERE


class ExperimentType(models.TextChoices):
    AC = "Ac", "Acute (<24 hr)"
    ST = "St", "Short-term (1-30 days)"
    SB = "Sb", "Subchronic (30-90 days)"
    CH = "Ch", "Chronic (>90 days)"
    CA = "Ca", "Cancer"
    ME = "Me", "Mechanistic"
    RP = "Rp", "Reproductive"
    R1 = "1r", "1-generation reproductive"
    R2 = "2r", "2-generation reproductive"
    DV = "Dv", "Developmental"
    OT = "Ot", "Other"
    NR = "NR", "Not-reported"


class TrendResult(models.IntegerChoices):
    NA = 0, "not applicable"
    NS = 1, "not significant"
    S = 2, "significant"
    NR = 3, "not reported"
