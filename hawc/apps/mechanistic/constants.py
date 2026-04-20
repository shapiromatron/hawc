from django.db import models

from ..common.constants import NA, NR


class CompositionPurity(models.TextChoices):
    AG = "AG", "Analytical Grade"
    TG = "TG", "Technical Grade"
    NS = "NS", "Purity Not Specified"
    NA = "NA", "Not Applicable (e.g. In Silico Study)"
    OT = "OT", "Other"
