from enum import StrEnum

import pandas as pd
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from pydantic import ConfigDict
from rest_framework.response import Response
from reversion.models import Version

from ...common.helper import FlatExport
from ...common.serializers import PydanticDrfSerializer
from ..constants import EpiVersion
from ..models import Assessment


def versions_by_content_type(app_label: str, model: str, qs: QuerySet | None = None) -> QuerySet:
    if qs is None:
        qs = Version.objects.all()
    ct = ContentType.objects.get(app_label=app_label, model=model)
    return qs.filter(content_type=ct)


def versions_by_related_field(
    related_field: str, related_values: list, qs: QuerySet | None = None
) -> QuerySet:
    qs = Version.objects.all() if qs is None else qs
    ored_values = "|".join([str(id) for id in related_values])
    data_regex = (
        rf"[\"\']fields[\"\']\s*:\s*{{[^}}]*?[\"\']{related_field}[\"\']\s*:\s*({ored_values})\s*,"
    )
    return qs.filter(serialized_data__iregex=data_regex)


class AuditType(StrEnum):
    ASSESSMENT = "assessment"
    ANIMAL = "animal"
    EPI = "epi"
    ROB = "riskofbias"


class AssessmentAuditSerializer(PydanticDrfSerializer):
    assessment: Assessment
    type: AuditType

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_assessment_queryset(self):
        # assessments
        assess_qs = Version.objects.get_for_model(Assessment).filter(object_id=self.assessment.pk)

        # get assessment attachments
        attach_qs = versions_by_content_type("assessment", "attachment")
        attach_qs = versions_by_related_field(
            "content_type", [ContentType.objects.get_for_model(Assessment).id], attach_qs
        )
        attach_qs = versions_by_related_field("object_id", [self.assessment.pk], attach_qs)

        # get assessment datasets
        dataset_qs = versions_by_content_type("assessment", "dataset")
        dataset_qs = versions_by_related_field("assessment", [self.assessment.pk], dataset_qs)

        # get assessment dataset revisions
        dataset_revision_qs = versions_by_content_type("assessment", "datasetrevision")
        dataset_revision_qs = versions_by_related_field(
            "dataset", set(dataset_qs.values_list("object_id", flat=True)), dataset_revision_qs
        )

        # get assessment summary tables
        summary_table_qs = versions_by_content_type("summary", "summarytable")
        summary_table_qs = versions_by_related_field(
            "assessment", [self.assessment.pk], summary_table_qs
        )
        # get assessment visuals
        visual_qs = versions_by_content_type("summary", "visual")
        visual_qs = versions_by_related_field("assessment", [self.assessment.pk], visual_qs)
        # get assessment data pivots
        data_pivot_qs = versions_by_content_type("summary", "datapivot")
        data_pivot_qs = versions_by_related_field("assessment", [self.assessment.pk], data_pivot_qs)
        # get data pivot uploads
        data_pivot_upload_qs = versions_by_content_type("summary", "datapivotupload")
        data_pivot_upload_qs = data_pivot_upload_qs.filter(
            object_id__in=set(data_pivot_qs.values_list("object_id", flat=True))
        )
        # get data pivot queries
        data_pivot_query_qs = versions_by_content_type("summary", "datapivotquery")
        data_pivot_query_qs = data_pivot_query_qs.filter(
            object_id__in=set(data_pivot_qs.values_list("object_id", flat=True))
        )

        return (
            assess_qs
            | attach_qs
            | dataset_qs
            | dataset_revision_qs
            | summary_table_qs
            | visual_qs
            | data_pivot_qs
            | data_pivot_upload_qs
            | data_pivot_query_qs
        )

    def get_animal_queryset(self):
        # get assessment references
        reference_qs = versions_by_content_type("lit", "reference")
        reference_qs = versions_by_related_field("assessment", [self.assessment.pk], reference_qs)
        # get reference studies
        study_qs = versions_by_content_type("study", "study")
        study_qs = study_qs.filter(
            object_id__in=set(reference_qs.values_list("object_id", flat=True))
        )
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
        # get base endpoints
        base_endpoint_qs = versions_by_content_type("assessment", "baseendpoint")
        base_endpoint_qs = base_endpoint_qs.filter(
            object_id__in=set(endpoint_qs.values_list("object_id", flat=True))
        )

        return experiment_qs | animal_group_qs | endpoint_qs | base_endpoint_qs

    def get_epiv1_queryset(self):
        # get assessment references
        reference_qs = versions_by_content_type("lit", "reference")
        reference_qs = versions_by_related_field("assessment", [self.assessment.pk], reference_qs)
        # get reference studies
        study_qs = versions_by_content_type("study", "study")
        study_qs = study_qs.filter(
            object_id__in=set(reference_qs.values_list("object_id", flat=True))
        )
        # get study populations
        study_population_qs = versions_by_content_type("epi", "studypopulation")
        study_population_qs = versions_by_related_field(
            "study", set(study_qs.values_list("object_id", flat=True)), study_population_qs
        )
        # get study population outcomes
        outcome_qs = versions_by_content_type("epi", "outcome")
        outcome_qs = versions_by_related_field(
            "study_population",
            set(study_population_qs.values_list("object_id", flat=True)),
            outcome_qs,
        )
        # get study population exposures
        exposure_qs = versions_by_content_type("epi", "exposure")
        exposure_qs = versions_by_related_field(
            "study_population",
            set(study_population_qs.values_list("object_id", flat=True)),
            exposure_qs,
        )
        # get outcome results
        result_qs = versions_by_content_type("epi", "result")
        result_qs = versions_by_related_field(
            "outcome", set(outcome_qs.values_list("object_id", flat=True)), result_qs
        )

        return study_population_qs | outcome_qs | exposure_qs | result_qs

    def get_epiv2_queryset(self):
        # get assessment references
        reference_qs = versions_by_content_type("lit", "reference")
        reference_qs = versions_by_related_field("assessment", [self.assessment.pk], reference_qs)
        # get reference studies
        study_qs = versions_by_content_type("study", "study")
        study_qs = study_qs.filter(
            object_id__in=set(reference_qs.values_list("object_id", flat=True))
        )
        # get study designs
        design_qs = versions_by_content_type("epiv2", "design")
        design_qs = versions_by_related_field(
            "study", set(study_qs.values_list("object_id", flat=True)), design_qs
        )
        # get design chemicals
        chemical_qs = versions_by_content_type("epiv2", "chemical")
        chemical_qs = versions_by_related_field(
            "study", set(design_qs.values_list("object_id", flat=True)), chemical_qs
        )
        # get design exposures
        exposure_qs = versions_by_content_type("epiv2", "exposure")
        exposure_qs = versions_by_related_field(
            "design", set(design_qs.values_list("object_id", flat=True)), exposure_qs
        )
        # get design exposure levels
        exposure_level_qs = versions_by_content_type("epiv2", "exposurelevel")
        exposure_level_qs = versions_by_related_field(
            "design", set(design_qs.values_list("object_id", flat=True)), exposure_level_qs
        )
        # get design outcomes
        outcome_qs = versions_by_content_type("epiv2", "outcome")
        outcome_qs = versions_by_related_field(
            "design", set(design_qs.values_list("object_id", flat=True)), outcome_qs
        )
        # get design adjustment factors
        adjustment_factor_qs = versions_by_content_type("epiv2", "adjustmentfactor")
        adjustment_factor_qs = versions_by_related_field(
            "design", set(design_qs.values_list("object_id", flat=True)), adjustment_factor_qs
        )
        # get design data extractions
        data_extraction_qs = versions_by_content_type("epiv2", "dataextraction")
        data_extraction_qs = versions_by_related_field(
            "design", set(design_qs.values_list("object_id", flat=True)), data_extraction_qs
        )

        return (
            design_qs
            | chemical_qs
            | exposure_qs
            | exposure_level_qs
            | outcome_qs
            | adjustment_factor_qs
            | data_extraction_qs
        )

    def get_riskofbias_queryset(self):
        # get assessment domains
        domain_qs = versions_by_content_type("riskofbias", "riskofbiasdomain")
        domain_qs = versions_by_related_field("assessment", [self.assessment.pk], domain_qs)
        # get domain metrics
        metric_qs = versions_by_content_type("riskofbias", "riskofbiasmetric")
        metric_qs = versions_by_related_field(
            "domain", set(domain_qs.values_list("object_id", flat=True)), metric_qs
        )
        # get metric scores
        score_qs = versions_by_content_type("riskofbias", "riskofbiasscore")
        score_qs = versions_by_related_field(
            "metric", set(metric_qs.values_list("object_id", flat=True)), score_qs
        )

        return domain_qs | metric_qs | score_qs

    def get_queryset(self):
        audit_type = self.type.value
        if audit_type == "epi":
            audit_type = "epiv1" if self.assessment.epi_version == EpiVersion.V1 else "epiv2"
        method = f"get_{audit_type}_queryset"
        qs = getattr(self, method)()
        return qs.select_related("content_type", "revision")

    def export(self) -> Response:
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
        return FlatExport.api_response(df=df, filename=f"{self.assessment}-{self.type}-audit-logs")
