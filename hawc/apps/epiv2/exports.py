import pandas as pd
from django.db.models import CharField, F, Func, QuerySet, Value

from ..common.exports import Exporter, ModelExport
from ..common.helper import FlatFileExporter
from ..common.models import sql_display, sql_format, str_m2m, to_display_array
from ..riskofbias.models import RiskOfBiasScore
from ..study.exports import StudyExport
from . import constants


class DesignExport(ModelExport):
    def get_value_map(self):
        return {
            "pk": "pk",
            "url": "url",
            "summary": "summary",
            "study_name": "study_name",
            "study_design": "study_design_display",
            "source": "source_display",
            "age_profile": "age_profile_string",
            "age_description": "age_description",
            "sex": "sex_display",
            "race": "race",
            "participant_n": "participant_n",
            "years_enrolled": "years_enrolled",
            "years_followup": "years_followup",
            "countries": "countries__name",
            "region": "region",
            "criteria": "criteria",
            "susceptibility": "susceptibility",
            "comments": "comments",
            "created": "created",
            "last_updated": "last_updated",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "url": sql_format("/epidemiology/design/{}/", query_prefix + "pk"),  # hardcoded URL
            "study_design_display": sql_display(
                query_prefix + "study_design", constants.StudyDesign
            ),
            "source_display": sql_display(query_prefix + "source", constants.Source),
            "age_profile_string": Func(
                F(query_prefix + "age_profile"),
                Value(", "),
                Value(""),
                function="array_to_string",
                output_field=CharField(max_length=256),
            ),
            "sex_display": sql_display(query_prefix + "sex", constants.Sex),
            "countries__name": str_m2m(query_prefix + "countries__name"),
        }

    def prepare_df(self, df):
        df.loc[:, self.get_column_name("age_profile")] = to_display_array(
            df[self.get_column_name("age_profile")], constants.AgeProfile, ", "
        )
        return df


class ChemicalExport(ModelExport):
    def get_value_map(self):
        return {
            "pk": "pk",
            "name": "name",
            "DTSXID": "dsstox__dtxsid",
            "created": "created",
            "last_updated": "last_updated",
        }


class ExposureExport(ModelExport):
    def get_value_map(self):
        return {
            "pk": "pk",
            "name": "name",
            "measurement_type": "measurement_type_string",
            "biomonitoring_matrix": "biomonitoring_matrix_display",
            "biomonitoring_source": "biomonitoring_source_display",
            "measurement_timing": "measurement_timing",
            "exposure_route": "exposure_route_display",
            "measurement_method": "measurement_method",
            "comments": "comments",
            "created": "created",
            "last_updated": "last_updated",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "measurement_type_string": Func(
                F(query_prefix + "measurement_type"),
                Value(", "),
                Value(""),
                function="array_to_string",
                output_field=CharField(max_length=256),
            ),
            "biomonitoring_matrix_display": sql_display(
                query_prefix + "biomonitoring_matrix",  # todo fix default display "?"
                constants.BiomonitoringMatrix,
            ),
            "biomonitoring_source_display": sql_display(
                query_prefix + "biomonitoring_source",  # todo fix default display "?"
                constants.BiomonitoringSource,
            ),
            "exposure_route_display": sql_display(
                query_prefix + "exposure_route", constants.ExposureRoute
            ),
        }


class ExposureLevelExport(ModelExport):
    def get_value_map(self):
        return {
            "pk": "pk",
            "name": "name",
            "sub_population": "sub_population",
            "median": "median",
            "mean": "mean",
            "variance": "variance",
            "variance_type": "variance_type_display",
            "units": "units",
            "ci_lcl": "ci_lcl",
            "percentile_25": "percentile_25",
            "percentile_75": "percentile_75",
            "ci_ucl": "ci_ucl",
            "ci_type": "ci_type_display",
            "negligible_exposure": "negligible_exposure",
            "data_location": "data_location",
            "comments": "comments",
            "created": "created",
            "last_updated": "last_updated",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "variance_type_display": sql_display(
                query_prefix + "variance_type", constants.VarianceType
            ),
            "ci_type_display": sql_display(
                query_prefix + "ci_type", constants.ConfidenceIntervalType
            ),
        }


class OutcomeExport(ModelExport):
    def get_value_map(self):
        return {
            "pk": "pk",
            "system": "system_display",
            "effect": "effect",
            "effect_detail": "effect_detail",
            "endpoint": "endpoint",
            "comments": "comments",
            "created": "created",
            "last_updated": "last_updated",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "system_display": sql_display(query_prefix + "system", constants.HealthOutcomeSystem),
        }


class AdjustmentFactorExport(ModelExport):
    def get_value_map(self):
        return {
            "pk": "pk",
            "name": "name",
            "description": "description",
            "comments": "comments",
            "created": "created",
            "last_updated": "last_updated",
        }


class DataExtractionExport(ModelExport):
    def get_value_map(self):
        return {
            "pk": "pk",
            "sub_population": "sub_population",
            "outcome_measurement_timing": "outcome_measurement_timing",
            "effect_estimate_type": "effect_estimate_type",
            "effect_estimate": "effect_estimate",
            "ci_lcl": "ci_lcl",
            "ci_ucl": "ci_ucl",
            "ci_type": "ci_type_display",
            "units": "units",
            "variance_type": "variance_type_display",
            "variance": "variance",
            "n": "n",
            "p_value": "p_value",
            "significant": "significant_display",
            "group": "group",
            "exposure_rank": "exposure_rank",
            "exposure_transform": "exposure_transform",
            "outcome_transform": "outcome_transform",
            "confidence": "confidence",
            "data_location": "data_location",
            "effect_description": "effect_description",
            "statistical_method": "statistical_method",
            "adverse_direction": "adverse_direction",
            "adverse_direction_display": "adverse_direction_display",
            "comments": "comments",
            "created": "created",
            "last_updated": "last_updated",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "ci_type_display": sql_display(
                query_prefix + "ci_type", constants.ConfidenceIntervalType
            ),
            "variance_type_display": sql_display(
                query_prefix + "variance_type", constants.VarianceType
            ),
            "significant_display": sql_display(query_prefix + "significant", constants.Significant),
            "adverse_direction_display": sql_display(
                query_prefix + "adverse_direction", constants.AdverseDirection
            ),
        }


class EpiV2Exporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport("study", "design__study"),
            DesignExport("design", "design"),
            ChemicalExport("chemical", "exposure_level__chemical"),
            ExposureExport("exposure", "exposure_level__exposure_measurement"),
            ExposureLevelExport("exposure_level", "exposure_level"),
            OutcomeExport("outcome", "outcome"),
            AdjustmentFactorExport("adjustment_factor", "factors"),
            DataExtractionExport("data_extraction", ""),
        ]


class EpiV2ExporterWithRob(EpiV2Exporter):
    def study_evaluation_data(self, df: pd.DataFrame) -> pd.DataFrame:
        qs = (
            RiskOfBiasScore.objects.filter(
                riskofbias__study__in=df["study-id"],
                metric__required_epi=True,
                riskofbias__final=True,
                riskofbias__active=True,
                is_default=True,
            )
            .data_pivot_json()
            .annotate(metric_column=sql_format("RoB ({})", "metric__name"))
            .values_list("riskofbias__study_id", "metric_id", "metric_column", "score_json")
        )
        if qs.count() == 0:
            return df

        rob_df = (
            pd.DataFrame(data=qs, columns=["study-id", "m-id", "metric_name", "rob_score_json"])
            .pivot(index=["study-id"], columns=["m-id", "metric_name"])["rob_score_json"]
            .droplevel(0, axis=1)
            .reset_index()
        )
        return df.merge(rob_df, how="left", on="study-id")

    def get_df(self, qs: QuerySet) -> pd.DataFrame:
        df = super().get_df(qs)
        df = self.study_evaluation_data(df)
        return df


class EpiFlatComplete(FlatFileExporter):
    """
    Returns a complete export of all data required to rebuild the the
    epidemiological meta-result study type from scratch.
    """

    def build_df(self) -> pd.DataFrame:
        return EpiV2ExporterWithRob().get_df(self.queryset)
