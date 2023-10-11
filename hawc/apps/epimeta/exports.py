import pandas as pd

from ..common.exports import Exporter, ModelExport
from ..common.helper import FlatFileExporter
from ..common.models import sql_display, sql_format, str_m2m
from ..epi.exports import ResultMetricExport
from ..study.exports import StudyExport
from . import constants


class MetaProtocolExport(ModelExport):
    def get_value_map(self):
        return {
            "pk": "pk",
            "url": "url",
            "name": "name",
            "protocol_type": "protocol_type",
            "lit_search_strategy": "lit_search_strategy",
            "lit_search_notes": "lit_search_notes",
            "lit_search_start_date": "lit_search_start_date",
            "lit_search_end_date": "lit_search_end_date",
            "total_references": "total_references",
            "inclusion_criteria": "inclusion_criteria",
            "exclusion_criteria": "exclusion_criteria",
            "total_studies_identified": "total_studies_identified",
            "notes": "notes",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "url": sql_format("/epi-meta/protocol/{}/", query_prefix + "id"),  # hardcoded URL
            "protocol_type": sql_display(query_prefix + "protocol_type", constants.MetaProtocol),
            "lit_search_strategy": sql_display(
                query_prefix + "lit_search_strategy", constants.MetaLitSearch
            ),
            "inclusion_criteria": str_m2m(query_prefix + "inclusion_criteria__description"),
            "exclusion_criteria": str_m2m(query_prefix + "exclusion_criteria__description"),
        }

    def prepare_df(self, df):
        for key in [
            self.get_column_name("lit_search_start_date"),
            self.get_column_name("lit_search_end_date"),
        ]:
            if key in df.columns:
                df.loc[:, key] = df[key].apply(lambda x: x.isoformat() if not pd.isna(x) else x)
        return df


class MetaResultExport(ModelExport):
    def get_value_map(self):
        return {
            "pk": "pk",
            "url": "url",
            "label": "label",
            "data_location": "data_location",
            "health_outcome": "health_outcome",
            "health_outcome_notes": "health_outcome_notes",
            "exposure_name": "exposure_name",
            "exposure_details": "exposure_details",
            "number_studies": "number_studies",
            "statistical_metric": "metric__metric",
            "statistical_notes": "statistical_notes",
            "n": "n",
            "estimate": "estimate",
            "lower_ci": "lower_ci",
            "upper_ci": "upper_ci",
            "ci_units": "ci_units",
            "heterogeneity": "heterogeneity",
            "adjustment_factors": "adjustment_factors_str",
            "notes": "notes",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "url": sql_format("/epi-meta/result/{}/", query_prefix + "id"),  # hardcoded URL
            "adjustment_factors_str": str_m2m(query_prefix + "adjustment_factors__description"),
        }


class SingleResultExport(ModelExport):
    def get_value_map(self):
        return {
            "pk": "pk",
            "study": "study_id",
            "exposure_name": "exposure_name",
            "weight": "weight",
            "n": "n",
            "estimate": "estimate",
            "lower_ci": "lower_ci",
            "upper_ci": "upper_ci",
            "ci_units": "ci_units",
            "notes": "notes",
        }


class EpiMetaExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport("study", "protocol__study"),
            MetaProtocolExport("meta_protocol", "protocol"),
            MetaResultExport("meta_result", ""),
            SingleResultExport("single_result", "single_results"),
        ]


class EpiMetaDataPivotExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport(
                "study",
                "protocol__study",
                include=(
                    "id",
                    "short_citation",
                    "published",
                ),
            ),
            MetaProtocolExport(
                "meta_protocol",
                "protocol",
                include=(
                    "pk",
                    "name",
                    "protocol_type",
                    "total_references",
                    "total_studies_identified",
                ),
            ),
            MetaResultExport(
                "meta_result",
                "",
                include=(
                    "pk",
                    "label",
                    "health_outcome",
                    "exposure_name",
                    "number_studies",
                    "n",
                    "estimate",
                    "lower_ci",
                    "upper_ci",
                    "ci_units",
                    "heterogeneity",
                ),
            ),
            ResultMetricExport(
                "metric",
                "metric",
                include=(
                    "name",
                    "abbreviation",
                ),
            ),
        ]


class MetaResultFlatComplete(FlatFileExporter):
    """
    Returns a complete export of all data required to rebuild the the
    epidemiological meta-result study type from scratch.
    """

    def build_df(self) -> pd.DataFrame:
        return EpiMetaExporter().get_df(self.queryset)


class MetaResultFlatDataPivot(FlatFileExporter):
    """
    Return a subset of frequently-used data for generation of data-pivot
    visualizations.

    Note: data pivot does not currently include study confidence. Could be added if needed.
    """

    def build_df(self) -> pd.DataFrame:
        df = EpiMetaDataPivotExporter().get_df(self.queryset)

        df["key"] = df["meta_result-pk"]

        df = df.rename(
            columns={
                "study-id": "study id",
                "study-short_citation": "study name",
                "study-published": "study published",
                "meta_protocol-pk": "protocol id",
                "meta_protocol-name": "protocol name",
                "meta_protocol-protocol_type": "protocol type",
                "meta_protocol-total_references": "total references",
                "meta_protocol-total_studies_identified": "identified references",
                "meta_result-pk": "meta result id",
                "meta_result-label": "meta result label",
                "meta_result-health_outcome": "health outcome",
                "meta_result-exposure_name": "exposure",
                "meta_result-number_studies": "result references",
                "metric-name": "statistical metric",
                "metric-abbreviation": "statistical metric abbreviation",
                "meta_result-n": "N",
                "meta_result-estimate": "estimate",
                "meta_result-lower_ci": "lower CI",
                "meta_result-upper_ci": "upper CI",
                "meta_result-ci_units": "CI units",
                "meta_result-heterogeneity": "heterogeneity",
            },
            errors="raise",
        )
        return df
