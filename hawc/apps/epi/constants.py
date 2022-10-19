from django.db import models

from ..common.constants import NO_LABEL


class CriteriaType(models.TextChoices):
    I = "I", "Inclusion"  # noqa: E741
    E = "E", "Exclusion"
    C = "C", "Confounding"


class Design(models.TextChoices):
    CO = "CO", "Cohort"
    CX = "CX", "Cohort (Retrospective)"
    CY = "CY", "Cohort (Prospective)"
    CC = "CC", "Case-control"
    NC = "NC", "Nested case-control"
    CR = "CR", "Case report"
    SE = "SE", "Case series"
    RT = "RT", "Randomized controlled trial"
    NT = "NT", "Non-randomized controlled trial"
    CS = "CS", "Cross-sectional"
    EC = "EC", "Ecological"
    OT = "OT", "Other"


class Diagnostic(models.IntegerChoices):
    NR = 0, "not reported"
    MPT = 1, "medical professional or test"
    MR = 2, "medical records"
    SR = 3, "self-reported"
    QU = 4, "questionnaire"
    HA = 5, "hospital admission"
    RE = 7, "registry"
    OT = 6, "other"


class Sex(models.TextChoices):
    U = "U", "Not reported"
    M = "M", "Male"
    F = "F", "Female"
    B = "B", "Male and Female"


IS_CONTROL_CHOICES = (
    (True, "Yes"),
    (False, "No"),
    (None, "N/A"),
)


class EstimateType(models.IntegerChoices):
    NONE = 0, NO_LABEL
    MEAN = 1, "mean"
    GMEAN = 2, "geometric mean"
    MEDIAN = 3, "median"
    POINT = 5, "point"
    OT = 4, "other"


class VarianceType(models.IntegerChoices):
    NONE = 0, NO_LABEL
    SD = 1, "SD"
    SE = 2, "SE"
    SEM = 3, "SEM"
    GSD = 4, "GSD"
    OT = 5, "other"


class GroupMeanType(models.IntegerChoices):
    NONE = 0, NO_LABEL
    MEAN = 1, "mean"
    GMEAN = 2, "geometric mean"
    MEDIAN = 3, "median"
    OT = 4, "other"


class GroupVarianceType(models.IntegerChoices):
    NONE = 0, NO_LABEL
    SD = 1, "SD"
    SEM = 2, "SEM"
    GSD = 3, "GSD"
    OT = 4, "other"


class LowerLimit(models.IntegerChoices):
    NONE = 0, NO_LABEL
    LL = 1, "lower limit"
    CI = 2, "5% CI"
    OT = 3, "other"


class UpperLimit(models.IntegerChoices):
    NONE = 0, NO_LABEL
    UL = 1, "upper limit"
    CI = 2, "95% CI"
    OT = 3, "other"


class DoseResponse(models.IntegerChoices):
    NA = 0, "not-applicable"
    MON = 1, "monotonic"
    NM = 2, "non-monotonic"
    NT = 3, "no trend"
    NR = 4, "not reported"


class StatisticalPower(models.IntegerChoices):
    NR = 0, "not reported or calculated"
    ADEQUATELY_POWERED = 1, "appears to be adequately powered (sample size met)"
    SOMEWHAT_UNDERPOWERED = 2, "somewhat underpowered (sample size is 75% to <100% of recommended)"
    UNDERPOWERED = 3, "underpowered (sample size is 50 to <75% required)"
    SEVERELY_UNDERPOWERED = 4, "severely underpowered (sample size is <50% required)"


class PValueQualifier(models.TextChoices):
    NONE = " ", "-"
    NS = "-", "n.s."
    LT = "<", "<"
    EQ = "=", "="
    GT = ">", ">"


class MainFinding(models.IntegerChoices):
    NR = 3, "not-reported"
    S = 2, "supportive"
    I = 1, "inconclusive"  # noqa: E741
    NS = 0, "not-supportive"
