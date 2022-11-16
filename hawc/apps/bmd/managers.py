from ..common.models import BaseManager


class AssessmentSettingsManager(BaseManager):
    assessment_relation = "assessment"


class SessionManager(BaseManager):
    assessment_relation = "endpoint__assessment"


class ModelManager(BaseManager):
    assessment_relation = "session__endpoint__assessment"


class SelectedModelManager(BaseManager):
    assessment_relation = "endpoint__assessment"
