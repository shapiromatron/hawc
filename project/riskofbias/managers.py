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
        return self.get_qs(assessment).filter(requireds)

    def get_metrics_for_visuals(self, assessment_id):
        return self.get_qs(assessment_id).values('id', 'name')


class RiskOfBiasManager(BaseManager):
    assessment_relation = 'study__assessment'

    def all_active(self, assessment=None):
        return self.get_qs(assessment).filter(active=True)

    def active(self, assessment=None):
        return self.get_qs(assessment).filter(active=True, final=False)

    def final(self, assessment=None):
        return self.get_qs(assessment).filter(final=True)


class RiskOfBiasScoreManager(BaseManager):
    assessment_relation = 'riskofbias__study__assessment'


class RiskOfBiasAssessmentManager(BaseManager):
    assessment_relation = 'assessment'
