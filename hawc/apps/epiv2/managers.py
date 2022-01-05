from ..common.models import BaseManager


class CriteriaManager(BaseManager):
    assessment_relation = "assessment"


# class AgeProfileManger(BaseManager):
#     assessment_relation = "studypopulation__study__assessment"


class CountryManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"

    def assessment_qs(self, assessment_id):
        qs = super().assessment_qs(assessment_id)
        return qs.distinct()
