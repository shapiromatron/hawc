import pandas as pd
from django.conf import settings
from django.db.models import Value

from ..common.exports import Exporter, ModelExport
from ..common.helper import cleanHTML
from ..common.models import sql_format
from ..study.exports import StudyExport
from . import constants


class RiskOfBiasExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "active": "active",
            "final": "final",
            "author_id": "author_id",
            "author_name": "author_full_name",
            "created": "created",
            "last_updated": "last_updated",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "author_full_name": sql_format(
                "{} {}", query_prefix + "author__first_name", query_prefix + "author__last_name"
            ),
        }

    def prepare_df(self, df):
        return self.format_time(df)


class DomainExport(ModelExport):
    def get_value_map(self):
        return {
            "domain_id": "id",
            "domain_name": "name",
            "domain_description": "description",
        }


class MetricExport(ModelExport):
    def get_value_map(self):
        return {
            "metric_id": "id",
            "metric_name": "name",
            "metric_description": "description",
        }


class RiskOfBiasScoreExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "is_default": "is_default",
            "label": "label",
            "score": "score",
            "description": Value("?"),
            "bias_direction": "bias_direction",
            "notes": "notes",
        }

    def prepare_df(self, df: pd.DataFrame) -> pd.DataFrame:
        if (key := self.get_column_name("description")) in df.columns:
            df.loc[:, key] = df[self.get_column_name("score")].map(constants.SCORE_CHOICES_MAP)
        if (key := self.get_column_name("notes")) in df.columns:
            df.loc[:, key] = df[key].apply(cleanHTML)
        return df


class RiskOfBiasExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport("study", "riskofbias__study"),
            RiskOfBiasExport(
                "rob", "riskofbias", exclude=("active", "final", "author_id", "author_name")
            ),
            DomainExport("rob", "metric__domain"),
            MetricExport("rob", "metric"),
            RiskOfBiasScoreExport("rob_score", ""),
        ]

    @classmethod
    def build_metadata(cls, df: pd.DataFrame) -> pd.DataFrame | None:
        fn = settings.PROJECT_PATH / "apps/riskofbias/data/exports/RiskOfBiasFlatSchema.tsv"
        return pd.read_csv(fn, delimiter="\t")


class RiskOfBiasCompleteExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport("study", "riskofbias__study"),
            RiskOfBiasExport("rob", "riskofbias"),
            DomainExport("rob", "metric__domain"),
            MetricExport("rob", "metric"),
            RiskOfBiasScoreExport("rob_score", ""),
        ]

    @classmethod
    def build_metadata(cls, df: pd.DataFrame) -> pd.DataFrame | None:
        fn = settings.PROJECT_PATH / "apps/riskofbias/data/exports/RiskOfBiasCompleteFlatSchema.tsv"
        return pd.read_csv(fn, delimiter="\t")
