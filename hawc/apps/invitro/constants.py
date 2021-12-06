from django.db import models


class Sex(models.TextChoices):
    M = "m", "Male"
    F = "f", "Female"
    MF = "mf", "Male and female"
    NA = "na", "Not-applicable"
    NR = "nr", "Not-reported"


class CultureType(models.TextChoices):
    NR = "nr", "not reported"
    IM = "im", "Immortalized cell line"
    PC = "pc", "Primary culture"
    TT = "tt", "Transient transfected cell line"
    ST = "st", "Stably transfected cell line"
    TS = "ts", "Transient transfected into stably transfected cell line"
    NA = "na", "not applicable"


class MetabolicActivation(models.TextChoices):
    W = "+", "with metabolic activation"
    WO = "-", "without metabolic activation"
    NA = "na", "not applicable"
    NR = "nr", "not reported"


class VarianceType(models.IntegerChoices):
    NA = 0, "NA"
    SD = 1, "SD"
    SE = 2, "SE"


class DataType(models.TextChoices):
    C = "C", "Continuous"
    D = "D", "Dichotomous"
    NR = "NR", "Not reported"


class Monotonicity(models.IntegerChoices):
    NR = 8, "--"
    SDLS = 0, "N/A, single dose level study"
    NED = 1, "N/A, no effects detected"
    VAM = 2, "visual appearance of monotonicity"
    MST = 3, "monotonic and significant trend"
    VANM = 4, "visual appearance of non-monotonicity"
    NPU = 6, "no pattern/unclear"


class OverallPattern(models.IntegerChoices):
    NA = 0, "not-available"
    I = 1, "increase"  # noqa: E741
    ITD = 2, "increase, then decrease"
    ITNC = 6, "increase, then no change"
    D = 3, "decrease"
    DTI = 4, "decrease, then increase"
    DTNC = 7, "decrease, then no change"
    NCP = 5, "no clear pattern"
    NC = 8, "no change"


class TrendTestResult(models.IntegerChoices):
    NR = 0, "not reported"
    NAN = 1, "not analyzed"
    NAP = 2, "not applicable"
    S = 3, "significant"
    NS = 4, "not significant"


class ObservationTimeUnits(models.IntegerChoices):
    NR = 0, "not-reported"
    S = 1, "seconds"
    MIN = 2, "minutes"
    H = 3, "hours"
    D = 4, "days"
    W = 5, "weeks"
    MON = 6, "months"


class DifferenceControl(models.TextChoices):
    NC = "nc", "no-change"
    D = "-", "decrease"
    I = "+", "increase"  # noqa: E741
    NT = "nt", "not-tested"


class Significance(models.TextChoices):
    NR = "nr", "not reported"
    SI = "si", "p ≤ 0.05"
    NS = "ns", "not significant"
    NA = "na", "not applicable"


OBSERVATION_CHOICES = (
    (None, "not reported"),
    (False, "not observed"),
    (True, "observed"),
)
