from django.db.models import Q, Manager, Count


class AssessmentTermQuery:
    def __init__(self, assessment_id):
        self.system = Q(
            endpoint_system_terms__animal_group__experiment__study__reference_ptr__assessment_id=assessment_id
        )
        self.organ = Q(
            endpoint_organ_terms__animal_group__experiment__study__reference_ptr__assessment_id=assessment_id
        )
        self.effect = Q(
            endpoint_effect_terms__animal_group__experiment__study__reference_ptr__assessment_id=assessment_id
        )
        self.effect_subtype = Q(
            endpoint_effect_subtype_terms__animal_group__experiment__study__reference_ptr__assessment_id=assessment_id
        )
        self.endpoint_name = Q(
            endpoint_name_terms__animal_group__experiment__study__reference_ptr__assessment_id=assessment_id
        )
        self.all = self.system | self.organ | self.effect | self.effect_subtype | self.endpoint_name


class TermManager(Manager):
    def assessment_systems(self, assessment_id):
        query = AssessmentTermQuery(assessment_id).system
        return (
            self.get_queryset()
            .filter(query)
            .annotate(count=Count("endpoint_system_terms", filter=query))
        )

    def assessment_all(self, assessment_id):
        query = AssessmentTermQuery(assessment_id).all
        return self.get_queryset().filter(query)

