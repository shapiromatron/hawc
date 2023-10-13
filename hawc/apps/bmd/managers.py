from ..common.models import BaseManager


class AssessmentSettingsManager(BaseManager):
    assessment_relation = "assessment"


class SessionManager(BaseManager):
    assessment_relation = "endpoint__assessment"
