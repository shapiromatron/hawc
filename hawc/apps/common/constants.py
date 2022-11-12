from django.db.models import IntegerChoices

NO_LABEL = "---"
NA = "N/A"
NR = "NR"


class AssessmentViewPermissions(IntegerChoices):
    PROJECT_MANAGER = 1
    TEAM_MEMBER = 2
    VIEWER = 3
