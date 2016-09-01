from django.db import models

from utils.models import BaseManager


class RiskOfBiasDomainManager(BaseManager):
    assessment_relation = 'assessment'


class RiskOfBiasMetricManager(BaseManager):
    assessment_relation = 'domain__assessment'

    def get_required_metrics(self, assessment, study):
        requireds = models.Q()
        if study.bioassay:
            requireds |= models.Q(required_animal=True)
        if study.epi or study.epi_meta:
            requireds |= models.Q(required_epi=True)

        return self.filter(domain__assessment=assessment)\
            .filter(requireds)

    def get_metrics_for_visuals(self, assessment_id):
        return self.filter(domain__assessment_id=assessment_id)\
            .values('id', 'metric')


class RiskOfBiasManager(BaseManager):
    assessment_relation = 'study__assessment'


class RiskOfBiasScoreManager(BaseManager):
    assessment_relation = 'riskofbias__study__assessment'


class RiskOfBiasAssessmentManager(BaseManager):
    assessment_relation = 'assessment'
