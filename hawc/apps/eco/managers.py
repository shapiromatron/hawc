from ..common.models import BaseManager


class DesignManager(BaseManager):
    assessment_relation = "study__assessment"


class CauseManager(BaseManager):
    assessment_relation = "study__assessment"


class EffectManager(BaseManager):
    assessment_relation = "study__assessment"


class ResultManager(BaseManager):
    assessment_relation = "design__study_assessment"
