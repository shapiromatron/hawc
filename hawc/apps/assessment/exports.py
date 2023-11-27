import pandas as pd

from ..common.exports import Exporter, ModelExport
from ..common.helper import FlatFileExporter
from .models import AssessmentValue


class ValuesListExport(FlatFileExporter):
    def build_df(self) -> pd.DataFrame:
        return AssessmentValue.objects.get_df()


class AssessmentValueExport(ModelExport):
    def get_value_map(self) -> dict:
        return {
            "pk": "pk",
            "evaluation_type": "evaluation_type",
            "system": "system",
        }


class AssessmentExport(ModelExport):
    def get_value_map(self) -> dict:
        return {"id": "id", "name": "name"}


class AssessmentDetail(ModelExport):
    def get_value_map(self) -> dict:
        return {"id": "id"}


class AssessmentExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            AssessmentValueExport("assessment_value", ""),
            AssessmentExport("assessment", "assessment"),
            # AssessmentExport("assessment_detail", ""),
        ]
