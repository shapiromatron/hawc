from django.db.models import Q

from ..common.models import BaseManager, get_distinct_charfield_opts


class CriteriaManager(BaseManager):
    assessment_relation = "assessment"


class CountryManager(BaseManager):
    assessment_relation = "studypopulation__study__assessment"

    def assessment_qs(self, assessment_id):
        qs = super().assessment_qs(assessment_id)
        return qs.distinct()


class AdjustmentFactorManager(BaseManager):
    assessment_relation = "assessment"


class EthnicityManger(BaseManager):
    def assessment_qs(self, assessment_id):
        return self.all()


class StudyPopulationCriteriaManager(BaseManager):
    assessment_relation = "criteria__assessment"


class StudyPopulationManager(BaseManager):
    assessment_relation = "study__assessment"


class OutcomeManager(BaseManager):
    assessment_relation = "assessment"

    def published(self, assessment_id=None):
        return self.get_qs(assessment_id).filter(study_population__study__published=True)

    def get_system_choices(self, assessment_id):
        return get_distinct_charfield_opts(self, assessment_id, "system")

    def get_effect_choices(self, assessment_id):
        return get_distinct_charfield_opts(self, assessment_id, "effect")


class ComparisonSetManager(BaseManager):
    def assessment_qs(self, assessment_id):
        return self.filter(
            Q(study_population__study__assessment=assessment_id)
            | Q(outcome__assessment=assessment_id)
        )


class GroupManager(BaseManager):
    def assessment_qs(self, assessment_id):
        return self.filter(
            Q(comparison_set__study_population__study__assessment=assessment_id)
            | Q(comparison_set__outcome__assessment=assessment_id)
        )


class ExposureManager(BaseManager):
    assessment_relation = "study_population__study__assessment"


class GroupNumericalDescriptionsManager(BaseManager):
    def assessment_qs(self, assessment_id):
        return self.filter(
            Q(group__comparison_set__study_population__study__assessment=assessment_id)
            | Q(group__comparison_set__outcome__assessment=assessment_id)
        )


class ResultMetricManager(BaseManager):
    def assessment_qs(self, assessment_id):
        return self.filter(
            Q(results__outcome__assessment=assessment_id)
            | Q(metaresult__protocol__study__assessment=assessment_id)
        ).distinct()


class ResultAdjustmentFactorManager(BaseManager):
    assessment_relation = "adjustment_factor__assessment"


class ResultManager(BaseManager):
    assessment_relation = "outcome__assessment"


class GroupResultManager(BaseManager):
    assessment_relation = "result__outcome__assessment"
