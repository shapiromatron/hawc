from django.db import models


class Sex(models.TextChoices):
    U = "U", "Not reported"
    M = "M", "Male"
    F = "F", "Female"
    B = "B", "Male and Female"


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
    OT = "OT", "Other"
    # TODO: include choices for effect estimate type


class CentralTendencyType(models.TextChoices):
    MEDIAN = "MED", "Median"
    # TODO: include other choices for central tendency


class ExposureRoute(models.TextChoices):
    IH = "IH", "Inhalation"
    OR = "OR", "Oral"
    DE = "DE", "Dermal"
    IU = "IU", "In utero"
    IV = "IV", "Intravenous"
    UK = "UK", "Unknown/Total"


class HealthOutcomeSystem(models.TextChoices):
    RE = "RE", "Reproductive"
    # TODO: include other choices for health outcome system


SIGNIFICANT_CHOICES = (
    (True, "Yes"),
    (False, "No"),
    (None, "N/A"),
)
