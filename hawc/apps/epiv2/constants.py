from django.db import models

from ..common.constants import NO_LABEL


class Sex(models.TextChoices):
    UNKNOWN = "U", "Not reported"
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    BOTH = "B", "Male and Female"


class StudyDesign(models.TextChoices):
    CO = "CO", "Cohort"
    CC = "CC", "Case-control"
    NC = "NC", "Nested case-control"
    CR = "CR", "Case report"
    SE = "SE", "Case series"
    RT = "RT", "Randomized controlled trial"
    NT = "NT", "Non-randomized controlled trial"
    CS = "CS", "Cross-sectional"
    OT = "OT", "Other"


class Source(models.TextChoices):
    GP = "GP", "General population"
    OC = "OC", "Occupational"
    OT = "OT", "Other"


class AgeProfile(models.TextChoices):
    AD = "AD", "Adults"
    CH = "CH", "Children and adolescents <18 yrs"
    PW = "PW", "Pregnant women"
    OT = "OT", "Other"


class EffectEstimateType(models.TextChoices):
    OR = "OR", "Odds Ratio (OR)"
    RR = "RR", "Relative Risk Ratio (RR)"
    AR = "AR", "Absolute Risk %"
    B = "B", "Regression coeffcient (β)"
    SMR = "SMR", "Standardized Mortality Ratio (SMR)"
    SIR = "SIR", "Standardized Incidence Ratio (SIR)"
    IRR = "IRR", "Incidence Risk Ratio (IRR)"
    ARR = "ARR", "Absolute Risk Reduction/ Risk difference (ARR or RD)"
    HR = "HR", "Hazard Ratio (HR)"
    CM = "CM", "Comparison of Means"
    SCC = "SCC", "Spearman's Correlation Coefficient"
    PC = "PC", "Percent change"
    MD = "MD", "Mean difference"


class VarianceType(models.IntegerChoices):
    NONE = 0, NO_LABEL
    SD = 1, "SD"
    SE = 2, "SE"
    SEM = 3, "SEM"
    GSD = 4, "GSD"
    OT = 5, "other"


class ConfidenceIntervalType(models.TextChoices):
    RNG = "Rng", "Range [min, max]"
    P95 = "P95", "5th/95th percentile"
    P99 = "P99", "1st/99th percentile"


class MeasurementType(models.TextChoices):
    BM = "BM", "Biomonitoring"
    AR = "AR", "Air"
    FD = "FD", "Food"
    DW = "DW", "Drinking water"
    OC = "OC", "Occupational"
    MD = "MD", "Modeled"
    QN = "QN", "Questionnaire"
    DO = "DO", "Direct administration - oral"
    DI = "DI", "Direct administration - inhalation"
    OT = "OT", "Other"


class ExposureRoute(models.TextChoices):
    IH = "IH", "Inhalation"
    OR = "OR", "Oral"
    DE = "DE", "Dermal"
    IU = "IU", "In utero"
    IV = "IV", "Intravenous"
    UK = "UK", "Unknown/Total"


class HealthOutcomeSystem(models.TextChoices):
    CA = "CA", "Cancer"
    CV = "CV", "Cardiovascular"
    DE = "DE", "Dermal"
    DV = "DV", "Developmental"
    EN = "EN", "Endocrine"
    GI = "GI", "Gastrointestinal"
    HM = "HM", "Hematologic"
    HP = "HP", "Hepatic"
    IM = "IM", "Immune"
    MT = "MT", "Metabolic"
    MS = "MS", "Multi-System"
    MU = "MU", "Musculoskeletal"
    NV = "NV", "Nervous"
    OC = "OC", "Ocular"
    RP = "RP", "Reproductive"
    RS = "RS", "Respiratory"
    UR = "UR", "Urinary"
    WB = "WB", "Whole Body"
    OT = "OT", "Other"


class Significant(models.IntegerChoices):
    NO = 0, "No"
    YES = 1, "Yes"
    NA = 2, "N/A"
    NR = 3, "NR"


class BiomonitoringMatrix(models.TextChoices):
    BL_PLASMA = "BLP", "Blood (portion: Plasma)"
    BL_WHOLE = "BLW", "Blood (portion: Whole blood)"
    BL_SERUM = "BLS", "Blood (portion: Serum)"
    UR = "UR", "Urine"
    TE = "TE", "Teeth"
    NL = "NL", "Nails"
    SA = "SA", "Saliva"
    BM = "BM", "Breast milk"
    SE = "SE", "Semen"
    FC = "FC", "Feces"
    CF = "CF", "Cerebrospinal fluid"
    EB = "EB", "Exhaled breath"
    OT = "OT", "Other"


class BiomonitoringSource(models.TextChoices):
    PT = "PT", "From participant"
    ML = "ML", "Maternal"
    PL = "PL", "Paternal"
    CD = "CD", "Cord"
