from ..common.models import BaseManager


class SessionManager(BaseManager):
    assessment_relation = "endpoint__assessment"
