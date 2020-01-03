from utils.models import BaseManager


class MetaProtocolManager(BaseManager):
    assessment_relation = 'study__assessment'


class MetaResultManager(BaseManager):
    assessment_relation = 'protocol__study__assessment'

    def published(self, assessment_id):
        return self.assessment_qs(assessment_id)\
                    .filter(protocol__study__published=True)


class SingleResultManager(BaseManager):
    assessment_relation = 'meta_result__protocol__study__assessment'
