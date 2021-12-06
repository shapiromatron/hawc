from django.db import models


class TaskType(models.IntegerChoices):
    TYPE_PREPARATION = 10, "preparation"
    TYPE_EXTRACTION = 20, "extraction"
    TYPE_QA = 30, "qa/qc"
    TYPE_ROB = 40, "rob completed"


class TaskStatus(models.IntegerChoices):
    STATUS_NOT_STARTED = 10, "not started"
    STATUS_STARTED = 20, "started"
    STATUS_COMPLETED = 30, "completed"
    STATUS_ABANDONED = 40, "abandoned"
