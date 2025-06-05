from django.db.models import Manager

from ..common.models import BaseManager
from ..vocab.constants import ObservationStatus


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


class ObservationManager(Manager):
    def default_observation(self, profile, endpoint):
        reported_status = False
        tested_status = False

        if endpoint or profile.obs_status == ObservationStatus.REQ:
            reported_status = True
            tested_status = True
        if profile.obs_status in (ObservationStatus.REC, ObservationStatus.TR):
            reported_status = True
            tested_status = False

        default = self.model(
            endpoint=profile.endpoint, tested_status=tested_status, reported_status=reported_status
        )
        return default
