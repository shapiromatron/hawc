from django.db import models

from ..common.constants import NO_LABEL


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
    PB = "Pb", "Pubertal"
    OT = "Ot", "Other"
    NR = "NR", "Not-reported"


class PurityQualifier(models.TextChoices):
    GT = ">", ">"
    GTE = "≥", "≥"
    EQUALS = "=", "="
    NA = "", ""


class Sex(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    COMBINED = "C", "Combined"
    NR = "R", "Not reported"


class Generation(models.TextChoices):
    NA = "", "N/A (not generational-study)"
    P0 = "P0", "Parent-generation (P0)"
    F1 = "F1", "First-generation (F1)"
    F2 = "F2", "Second-generation (F2)"
    F3 = "F3", "Third-generation (F3)"
    F4 = "F4", "Fourth-generation (F4)"
    OT = "Ot", "Other"


class Lifestage(models.TextChoices):
    """
    Notes
    -----
    these choices for lifesage expose/assessed were added ~Sept 2018. B/c there are existing values
    in the database, we are not going to enforce these choices on the model as we do for say sex.
    Instead we'll leave the model as is, and start using this to drive a Select widget on the form.
    For old/existing data, we'll add the previously saved value to the dropdown at runtime so we don't lose data.
    """

    DEV = "Developmental", "Developmental"
    JUV = "Juvenile", "Juvenile"
    ADULT = "Adult", "Adult"
    AG = "Adult (gestation)", "Adult (gestation)"
    ML = "Multi-lifestage", "Multi-lifestage"


class RouteExposure(models.TextChoices):
    OR = "OR", "Oral"
    OC = "OC", "Oral capsule"
    OD = "OD", "Oral diet"
    OG = "OG", "Oral gavage"
    OW = "OW", "Oral drinking water"
    I = "I", "Inhalation"  # noqa: E741
    IG = "IG", "Inhalation - gas"
    IR = "IR", "Inhalation - particle"
    IA = "IA", "Inhalation - vapor"
    D = "D", "Dermal"
    SI = "SI", "Subcutaneous injection"
    IP = "IP", "Intraperitoneal injection"
    IV = "IV", "Intravenous injection"
    IO = "IO", "in ovo"
    P = "P", "Parental"
    W = "W", "Whole body"
    M = "M", "Multiple"
    U = "U", "Unknown"
    O = "O", "Other"  # noqa: E741


class NegativeControl(models.TextChoices):
    NR = "NR", "Not-reported"
    UN = "UN", "Untreated"
    VT = "VT", "Vehicle-treated"
    B = "B", "Untreated + Vehicle-treated"
    N = "N", "No"


class DataType(models.TextChoices):
    CONTINUOUS = "C", "Continuous"
    DICHOTOMOUS = "D", "Dichotomous"
    PERCENT_DIFFERENCE = "P", "Percent Difference"
    DICHOTOMOUS_CANCER = "DC", "Dichotomous Cancer"
    NR = "NR", "Not reported"


class Monotonicity(models.IntegerChoices):
    NR = 8, "--"
    SDLS = 0, "N/A, single dose level study"
    NED = 1, "N/A, no effects detected"
    VAM = 2, "visual appearance of monotonicity"
    MST = 3, "monotonic and significant trend"
    VANM = 4, "visual appearance of non-monotonicity"
    NPU = 6, "no pattern/unclear"


class VarianceType(models.IntegerChoices):
    NA = 0, "NA"
    SD = 1, "SD"
    SE = 2, "SE"
    NR = 3, "NR"


class ObservationTimeUnits(models.IntegerChoices):
    NR = 0, "not reported"
    SEC = 1, "seconds"
    MIN = 2, "minutes"
    HR = 3, "hours"
    DAY = 4, "days"
    WK = 5, "weeks"
    MON = 6, "months"
    YR = 9, "years"
    PND = 7, "post-natal day (PND)"
    GD = 8, "gestational day (GD)"


class TrendResult(models.IntegerChoices):
    NA = 0, "not applicable"
    NS = 1, "not significant"
    S = 2, "significant"
    NR = 3, "not reported"


class AdverseDirection(models.IntegerChoices):
    INC = 3, "increase from reference/control group"
    DEC = 2, "decrease from reference/control group"
    ANY = 1, "any change from reference/control group"
    U = 0, "unclear"
    NR = 4, NO_LABEL


class LitterEffect(models.TextChoices):
    NA = "NA", "Not applicable"
    NR = "NR", "Not reported"
    YS = "YS", "Yes, statistical control"
    YD = "YD", "Yes, study-design"
    N = "N", "No"
    O = "O", "Other"  # noqa: E741


class TreatmentEffect(models.IntegerChoices):
    NR = 0, "not reported"
    YES_UP = 1, "yes ↑"
    YES_DOWN = 2, "yes ↓"
    YES = 3, "yes"
    NO = 4, "no"


# bool can't be subclassed with models.Choices
POSITIVE_CONTROL_CHOICES = (
    (True, "Yes"),
    (False, "No"),
    (None, "Unknown"),
)
