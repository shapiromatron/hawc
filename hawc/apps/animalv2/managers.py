from ..common.models import BaseManager


class ExperimentManager(BaseManager):
    assessment_relation = "study__assessment"


class ChemicalManager(BaseManager):
    assessment_relation = "experiment__study__assessment"


class AnimalGroupManager(BaseManager):
    assessment_relation = "experiment__study__assessment"


class TreatmentManager(BaseManager):
    assessment_relation = "experiment__study__assessment"


class DoseGroupManager(BaseManager):
    assessment_relation = "treatment__experiment__study__assessment"


class EndpointManager(BaseManager):
    assessment_relation = "experiment__study__assessment"


class ObservationTimeManager(BaseManager):
    assessment_relation = "endpoint__experiment__study__assessment"


class DataExtractionManager(BaseManager):
    assessment_relation = "experiment__study__assessment"


class DoseResponseGroupLevelDataManager(BaseManager):
    assessment_relation = "data_extraction__experiment__study__assessment"


class DoseResponseAnimalLevelDataManager(BaseManager):
    assessment_relation = "data_extraction__experiment__study__assessment"
