from django.db.models import IntegerChoices

from ..assessment.permissions import AssessmentPermissions

NO_LABEL = "---"
NA = "N/A"
NR = "NR"


class AssessmentViewPermissions(IntegerChoices):
    PROJECT_MANAGER = 1
    TEAM_MEMBER = 2
    VIEWER = 3


class AssessmentViewSetPermissions(IntegerChoices):
    CAN_VIEW_OBJECT = 1
    CAN_EDIT_OBJECT = 2
    CAN_EDIT_ASSESSMENT = 3
    TEAM_MEMBER_OR_HIGHER = 4
    PROJECT_MANAGER_OR_HIGHER = 5

    def has_permission(self, assessment, user, **kwargs):
        perms = AssessmentPermissions.get(assessment)
        return getattr(perms, self.name.lower())(user, **kwargs)
