from django.db import models


class MetaProtocol(models.IntegerChoices):
    META = 0, "Meta-analysis"
    POOLED = 1, "Pooled-analysis"


class MetaLitSearch(models.IntegerChoices):
    SYSTEMATIC = 0, "Systematic"
    OTHER = 1, "Other"
