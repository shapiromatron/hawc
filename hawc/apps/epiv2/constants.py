from django.db import models


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
    OR = "OR", "Odds Ratio"
    PC = "PC", "Percent Change"
    OT = "OT", "Other"
    # TODO: include choices for effect estimate type


class UpperLowerType(models.TextChoices):
    MX = "MX", "Min/Max"
    N5 = "N5", "5/95"
    N9 = "N9", "1/99"


class ExposureRoute(models.TextChoices):
    IH = "IH", "Inhalation"
    OR = "OR", "Oral"
    DE = "DE", "Dermal"
    IU = "IU", "In utero"
    IV = "IV", "Intravenous"
    UK = "UK", "Unknown/Total"


class HealthOutcomeSystem(models.TextChoices):
    RE = "RE", "Reproductive"
    IM = "IM", "Immune"
    # TODO: include other choices for health outcome system


class Significant(models.IntegerChoices):
    NO = 0, "No"
    YES = 1, "Yes"
    NA = 2, "N/A"
