from django.db import models

from .permissions import AssessmentPermissions


class AssessmentViewPermissions(models.IntegerChoices):
    PROJECT_MANAGER = 1
    TEAM_MEMBER = 2
    VIEWER = 3


class AssessmentViewSetPermissions(models.IntegerChoices):
    CAN_VIEW_OBJECT = 1
    CAN_EDIT_OBJECT = 2
    CAN_EDIT_ASSESSMENT = 3
    TEAM_MEMBER_OR_HIGHER = 4
    PROJECT_MANAGER_OR_HIGHER = 5

    def has_permission(self, assessment, user, **kwargs):
        perms = AssessmentPermissions.get(assessment)
        return getattr(perms, self.name.lower())(user, **kwargs)


class NoelName(models.IntegerChoices):
    NEL = 2, "NEL/LEL"
    NOEL = 0, "NOEL/LOEL"
    NOAEL = 1, "NOAEL/LOAEL"


class RobName(models.IntegerChoices):
    ROB = 0, "Risk of bias"
    SE = 1, "Study evaluation"


class JobStatus(models.IntegerChoices):
    PENDING = 1, "PENDING"
    SUCCESS = 2, "SUCCESS"
    FAILURE = 3, "FAILURE"


class JobType(models.IntegerChoices):
    TEST = 1, "TEST"


class EpiVersion(models.IntegerChoices):
    V1 = 1, "v1"
    V2 = 2, "v2"
