from ..common.models import BaseManager


class AgeProfileManger(BaseManager):
    assessment_relation = "studypopulation__study__assessment"


class CriteriaManager(BaseManager):
    assessment_relation = "assessment"


class MeasurementTypeManager(BaseManager):
    assessment_relation = "assessment"


class DesignManager(BaseManager):
    assessment_relation = "study__assessment"


class ChemicalManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"


class ExposureManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"


class ExposureLevelManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"


class OutcomeManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"


class AdjustmentFactorManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"


class DataExtractionManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"
