from enum import Enum

import pandas as pd
from reversion.models import Version
from django.contrib.contenttypes.models import ContentType

from ..models import Assessment
from ...common.helper import FlatExport
from ...common.serializers import PydanticDrfSerializer


def versions_by_content_type(app_label: str, model: str, qs=None):
    qs = Version.objects.all() if qs is None else qs
    ct = ContentType.objects.get(app_label=app_label, model=model)
    return qs.filter(content_type=ct)


def versions_by_related_field(related_field: str, related_values: list, qs=None):
    qs = Version.objects.all() if qs is None else qs
    ored_values = "|".join([str(id) for id in related_values])
    data_regex = rf"[\"\']fields[\"\']\s*:\s*{{[^}}]*?[\"\']{related_field}[\"\']\s*:\s*({ored_values})\s*,"
    return qs.filter(serialized_data__iregex=data_regex)


class AuditType(str, Enum):
    ASSESSMENT = "assessment"
    ANIMAL = "animal"


class AssessmentAuditSerializer(PydanticDrfSerializer):
    assessment: Assessment
    type: AuditType

    class Config:
        arbitrary_types_allowed = True

    def get_assessment_queryset(self):
        return Version.objects.get_for_model(Assessment).filter(object_id=self.assessment.pk)

    def get_animal_queryset(self):
        reference_qs = versions_by_content_type("lit", "reference")
        reference_qs = versions_by_related_field("assessment", [self.assessment.pk], reference_qs)
        # get bioassay studies associated with references
        study_qs = versions_by_content_type("study", "study")
        study_qs = study_qs.filter(object_id__in=set(reference_qs.values_list("object_id", flat=True)))
        study_qs = versions_by_related_field("bioassay", ["true"], study_qs)
        # get study experiments
        experiment_qs = versions_by_content_type("animal", "experiment")
        experiment_qs = versions_by_related_field(
            "study", set(study_qs.values_list("object_id", flat=True)), experiment_qs
        )
        # get experiment animal groups
        animal_group_qs = versions_by_content_type("animal", "animalgroup")
        animal_group_qs = versions_by_related_field(
            "experiment", set(experiment_qs.values_list("object_id", flat=True)), animal_group_qs
        )
        # get animal group endpoints
        endpoint_qs = versions_by_content_type("animal", "endpoint")
        endpoint_qs = versions_by_related_field(
            "animal_group", set(animal_group_qs.values_list("object_id", flat=True)), endpoint_qs
        )
        return experiment_qs | animal_group_qs | endpoint_qs

    def get_queryset(self):
        qs = getattr(self, f"get_{self.type}_queryset")()
        return qs.select_related("content_type", "revision")

    def export(self) -> FlatExport:
        qs = self.get_queryset()
        df = pd.DataFrame(
            qs.values_list(
                "content_type__app_label",
                "content_type__model",
                "object_id",
                "serialized_data",
                "revision__user",
                "revision__date_created",
            ),
            columns=["app", "model", "pk", "serialized_data", "user", "date_revised"],
        )
        export = FlatExport(df=df, filename="merp")
        return export
