from utils.models import BaseManager


class IVChemicalManager(BaseManager):
    assessment_relation = 'study__assessment'

    def get_choices(self, assessment_id):
        return self.filter(study__assessment_id=assessment_id)\
            .order_by('name')\
            .distinct('name')\
            .values_list('name', 'name')


class IVCellTypeManager(BaseManager):
    assessment_relation = 'study__assessment'


class IVExperimentManager(BaseManager):
    assessment_relation = 'study__assessment'


class IVEndpointManager(BaseManager):
    assessment_relation = 'assessment'

    def published(self, assessment_id=None):
        return self.get_qs(assessment_id)\
                    .filter(experiment__study__published=True)


class IVEndpointGroupManager(BaseManager):
    assessment_relation = 'endpoint__assessment'


class IVBenchmarkManager(BaseManager):
    assessment_relation = 'endpoint__assessment'
