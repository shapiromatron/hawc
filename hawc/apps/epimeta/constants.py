from django.db import models


class MetaProtocol(models.IntegerChoices):
    MA = 0, "Meta-analysis"
    PA = 1, "Pooled-analysis"


class MetaLitSearch(models.IntegerChoices):
    SYS = 0, "Systematic"
    OT = 1, "Other"
