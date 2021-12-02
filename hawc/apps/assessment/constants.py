from django.db import models


class NoelName(models.IntegerChoices):
    NOEL = 0, "NOEL/LOEL"
    NOAEL = 1, "NOAEL/LOAEL"
    NEL = 2, "NEL/LEL"


class RobName(models.IntegerChoices):
    ROB = 0, "Risk of bias"
    SE = 1, "Study evaluation"


class JobStatus(models.IntegerChoices):
    PENDING = 0, "PENDING"
    SUCCESS = 2, "SUCCESS"
    FAILURE = 3, "FAILURE"


class JobType(models.IntegerChoices):
    TEST = 1, "TEST"
