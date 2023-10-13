from ..common.models import BaseManager


class IVChemicalManager(BaseManager):
    assessment_relation = "study__assessment"

    def get_choices(self, assessment_id):
        return (
            self.get_qs(assessment_id).order_by("name").distinct("name").values_list("name", "name")
        )


class IVCellTypeManager(BaseManager):
    assessment_relation = "study__assessment"


class IVExperimentManager(BaseManager):
    assessment_relation = "study__assessment"


class IVEndpointManager(BaseManager):
    assessment_relation = "assessment"

    def get_effect_choices(self, assessment_id):
        return (
            self.get_qs(assessment_id)
            .order_by("effect")
            .distinct("effect")
            .values_list("effect", "effect")
        )

    def published(self, assessment_id=None):
        return self.get_qs(assessment_id).filter(experiment__study__published=True)


class IVEndpointGroupManager(BaseManager):
    assessment_relation = "endpoint__assessment"


class IVBenchmarkManager(BaseManager):
    assessment_relation = "endpoint__assessment"
