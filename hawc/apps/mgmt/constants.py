from django.db import models


class TaskType(models.IntegerChoices):
    PREPARATION = 10, "preparation"
    EXTRACTION = 20, "extraction"
    QA = 30, "qa/qc"
    ROB = 40, "rob completed"


class TaskStatus(models.IntegerChoices):
    NOT_STARTED = 10, "not started"
    STARTED = 20, "started"
    COMPLETED = 30, "completed"
    ABANDONED = 40, "abandoned"
