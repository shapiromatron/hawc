import pandas as pd

from ..common.exports import Exporter, ModelExport
from ..common.helper import FlatFileExporter
from ..common.models import sql_display, sql_format, str_m2m
from ..study.exports import StudyExport
from . import constants
from .models import AssessmentValue


class ValuesListExport(FlatFileExporter):
    def build_df(self) -> pd.DataFrame:
        return AssessmentValue.objects.get_df()


class AssessmentValueExport(ModelExport):
    def get_value_map(self) -> dict:
        return {
            "evaluation_type": "evaluation_type_display",
            "system": "system",
            "value_type": "value_type_display",
            "value": "value",
            "value_unit": "value_unit",
            "confidence": "confidence",
            "pod_value": "pod_value",
            "pod_unit": "pod_unit",
            "tumor_type": "tumor_type",
            "extrapolation_method": "extrapolation_method",
            "comments": "comments",
            "extra": "extra",
        }

    def get_annotation_map(self, query_prefix: str) -> dict:
        return {
            "evaluation_type_display": sql_display(
                query_prefix + "evaluation_type", constants.EvaluationType
            ),
            "value_type_display": sql_display(query_prefix + "value_type", constants.ValueType),
        }


class AssessmentExport(ModelExport):
    def get_value_map(self) -> dict:
        return {"id": "id", "name": "name", "created": "created", "last_updated": "last_updated"}


class AssessmentDetailExport(ModelExport):
    def get_value_map(self) -> dict:
        return {
            "project_type": "project_type",
            "project_status": "project_status_display",
            "project_url": "project_url",
            "peer_review_status": "peer_review_status",
            "qa_id": "qa_id",
            "qa_url": "qa_url",
            "report_id": "report_id",
            "report_url": "report_url",
        }

    def get_annotation_map(self, query_prefix: str) -> dict:
        return {
            "project_status_display": sql_display(query_prefix + "project_status", constants.Status)
        }


class AssessmentExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            AssessmentExport("assessment", "assessment"),
            AssessmentDetailExport("assessment_detail", "assessment__details"),
            AssessmentValueExport("assessment_value", ""),
            StudyExport(
                "study",
                "study",
                include=(
                    "id",
                    "short_citation",
                    "published",
                ),
            ),
        ]
