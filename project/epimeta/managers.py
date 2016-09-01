from utils.models import BaseManager


class MetaProtocolManager(BaseManager):
    assessment_relation = 'study__assessment'


class MetaResultManager(BaseManager):
    assessment_relation = 'protocol__study__assessment'


class SingleResultManager(BaseManager):
    assessment_relation = 'meta_result__protocol__study__assessment'
