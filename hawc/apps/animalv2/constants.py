from django.db import models


class ExperimentDesign(models.TextChoices):
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


class Sex(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    COMBINED = "C", "Combined"
    NR = "R", "Not reported"


class Generation(models.TextChoices):
    NA = "", "N/A (not generational-study)"
    P0 = "P0", "Parent-generation (P0)"
    F0 = "F0", "First-generation (F0)"
    F1 = "F1", "First-generation (F1)"
    F2 = "F2", "Second-generation (F2)"
    F3 = "F3", "Third-generation (F3)"
    F4 = "F4", "Fourth-generation (F4)"
    OT = "Ot", "Other"


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


class VarianceType(models.IntegerChoices):
    NA = 0, "NA"
    SD = 1, "SD"
    SE = 2, "SE"
    NR = 3, "NR"


class TreatmentRelatedEffect(models.IntegerChoices):
    YES = 0, "Yes"
    NO = 1, "No"
    NA = 2, "NA"
    NR = 3, "NR"


class MethodToControlForLitterEffects(models.IntegerChoices):
    YES = 0, "Yes"
    NR = 1, "NR"
    NA = 2, "NA"


class DatasetType(models.TextChoices):  # TODO - nested dichotomous?
    CONTINUOUS = "C", "Continuous"
    DICHOTOMOUS = "D", "Dichotomous"
    PERCENT_DIFFERENCE = "PD", "Percent Difference"
    DICHOTOMOUS_CANCER = "DC", "Dichotomous Cancer"  # TODO - remove cancer?
    NOT_REPORTED = "NR", "Not reported"


class StatisticallySignificant(models.IntegerChoices):
    YES = 0, "Yes"
    NO = 1, "No"
    NA = 2, "NA"


class Lifestage(models.TextChoices):
    DEV = "DEV", "Developmental"
    JUV = "JUV", "Juvenile"
    ADULT = "ADULT", "Adult"
    AG = "AG", "Adult (gestation)"
    ML = "ML", "Multi-lifestage"


class StudyLevelTypeChoices(models.IntegerChoices):
    LOEL = 0, "LOEL"
    NOEL = 1, "NOEL"
    LOAEL = 2, "LOAEL"
    NOAEL = 3, "NOAEL"
    BMDL = 4, "BMDL"
    BMD = 5, "BMD"
