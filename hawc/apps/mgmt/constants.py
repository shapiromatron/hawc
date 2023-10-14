from django.db import models


class TaskType(models.IntegerChoices):
    PREPARATION = 10, "Preparation"
    EXTRACTION = 20, "Data Extraction"
    QA = 30, "QA/QC"
    ROB = 40, "Study Evaluation"


class TaskStatus(models.IntegerChoices):
    NOT_STARTED = 10, "not started"
    STARTED = 20, "started"
    COMPLETED = 30, "completed"
    ABANDONED = 40, "abandoned"
