from django.db.models import Q

from ..common.models import BaseManager, get_distinct_charfield_opts


class CriteriaManager(BaseManager):
    assessment_relation = "assessment"


class CountryManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"

    def assessment_qs(self, assessment_id):
        qs = super().assessment_qs(assessment_id)
        return qs.distinct()
