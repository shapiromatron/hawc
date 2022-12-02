from django.db.models import IntegerChoices, TextChoices


class VocabCategories(IntegerChoices):
    TYPE = 0, "Study type"
    SETTING = 1, "Study setting"
    HABITAT = 2, "Habitat"
    CAUSE_TERM = 3, "Cause term"
    CAUSE_MEASURE = 4, "Cause measure"
    BIO_ORG = 5, "Biological organization"
    EFFECT_TERM = 6, "Effect term"
    EFFECT_MEASURE = 7, "Effect measure"
    RESPONSE_MEASURETYPE = 8, "Response measure type"
    RESPONSE_VARIABILITY = 9, "Response variability"
    STATISTICAL = 10, "Statistical significance measure"
    CLIMATE = 11, "Climate"
    ECOREGION = 12, "Ecoregion"


class ChangeTrajectory(IntegerChoices):
    INCREASE = 0, "Increase"
    DECREASE = 1, "Decrease"
    CHANGE = 2, "Change"
    NOCHANGE = 3, "No change"
    MULTIPLE = 4, "Multiple"
    OTHER = 10, "Other"


class TypeChoices(TextChoices):
    CE = "CE", "cause/effect"
