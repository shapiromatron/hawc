import pandas as pd
from django.db.models import Case, CharField, Q, When
from django.db.models.functions import Cast

from ..common.exports import Exporter, ModelExport
from ..common.helper import FlatFileExporter
from ..common.models import sql_display, sql_format, str_m2m, to_display_array
from ..materialized.models import FinalRiskOfBiasScore
from ..study.exports import StudyExport
from ..study.models import Study
from . import constants, models


def format_time(model_export: ModelExport, df):
    df.loc[:, model_export.get_column_name("created")] = df[
        model_export.get_column_name("created")
    ].apply(lambda x: x.isoformat())
    df.loc[:, model_export.get_column_name("last_updated")] = df[
        model_export.get_column_name("last_updated")
    ].apply(lambda x: x.isoformat())
    return df


class StudyPopulationExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "url": "url",
            "name": "name",
            "design": "design_display",
            "age_profile": "age_profile",
            "source": "source",
            "countries": "countries__name",
            "region": "region",
            "state": "state",
            "eligible_n": "eligible_n",
            "invited_n": "invited_n",
            "participant_n": "participant_n",
            "inclusion_criteria": "inclusion_criteria",
            "exclusion_criteria": "exclusion_criteria",
            "confounding_criteria": "confounding_criteria",
            "comments": "comments",
            "created": "created",
            "last_updated": "last_updated",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "url": sql_format("/epi/study-population/{}/", query_prefix + "id"),  # hardcoded URL
            "design_display": sql_display(query_prefix + "design", constants.Design),
            "countries__name": str_m2m(query_prefix + "countries__name"),
            "inclusion_criteria": str_m2m(
                query_prefix + "spcriteria__criteria__description",
                filter=Q(**{query_prefix + "spcriteria__criteria_type": constants.CriteriaType.I}),
            ),
            "exclusion_criteria": str_m2m(
                query_prefix + "spcriteria__criteria__description",
                filter=Q(**{query_prefix + "spcriteria__criteria_type": constants.CriteriaType.E}),
            ),
            "confounding_criteria": str_m2m(
                query_prefix + "spcriteria__criteria__description",
                filter=Q(**{query_prefix + "spcriteria__criteria_type": constants.CriteriaType.C}),
            ),
        }

    def prepare_df(self, df):
        return df


class OutcomeExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "url": "url",
            "name": "name",
            "effects": "effects__name",
            "system": "system",
            "effect": "effect",
            "effect_subtype": "effect_subtype",
            "diagnostic": "diagnostic_display",
            "diagnostic_description": "diagnostic_description",
            "age_of_measurement": "age_of_measurement",
            "outcome_n": "outcome_n",
            "summary": "summary",
            "created": "created",
            "last_updated": "last_updated",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "url": sql_format("/epi/outcome/{}/", query_prefix + "id"),  # hardcoded URL
            "effects__name": str_m2m(query_prefix + "effects__name"),
            "diagnostic_display": sql_display(query_prefix + "diagnostic", constants.Diagnostic),
        }


class ExposureExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "url": "url",
            "name": "name",
            "inhalation": "inhalation",
            "dermal": "dermal",
            "oral": "oral",
            "in_utero": "in_utero",
            "iv": "iv",
            "unknown_route": "unknown_route",
            "measured": "measured",
            "metric": "metric",
            "metric_units_id": "metric_units__id",
            "metric_units_name": "metric_units__name",
            "metric_description": "metric_description",
            "analytical_method": "analytical_method",
            "sampling_period": "sampling_period",
            "age_of_exposure": "age_of_exposure",
            "duration": "duration",
            "n": "n",
            "exposure_distribution": "exposure_distribution",
            "description": "description",
            "created": "created",
            "last_updated": "last_updated",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "url": sql_format("/epi/exposure/{}/", query_prefix + "id"),  # hardcoded URL
        }


class ComparisonSetExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "url": "url",
            "name": "name",
            "description": "description",
            "created": "created",
            "last_updated": "last_updated",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "url": sql_format("/epi/comparison-set/{}/", query_prefix + "id"),  # hardcoded URL
        }


class ResultMetricExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "name": "metric",
            "abbreviation": "abbreviation",
        }


class ResultExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "name": "name",
            "metric_description": "metric_description",
            "metric_units": "metric_units",
            "data_location": "data_location",
            "population_description": "population_description",
            "dose_response": "dose_response_display",
            "dose_response_details": "dose_response_details",
            "prevalence_incidence": "prevalence_incidence",
            "statistical_power": "statistical_power_display",
            "statistical_power_details": "statistical_power_details",
            "statistical_test_results": "statistical_test_results",
            "trend_test": "trend_test",
            "adjustment_factors": "adjustment_factors",
            "adjustment_factors_considered": "adjustment_factors_considered",
            "estimate_type": "estimate_type_display",
            "variance_type": "variance_type_display",
            "ci_units": "ci_units",
            "comments": "comments",
            "created": "created",
            "last_updated": "last_updated",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "dose_response_type": sql_display(
                query_prefix + "dose_response", constants.DoseResponse
            ),
            "adjustment_factors": str_m2m(
                query_prefix + "resfactors__adjustment_factor__description",
                filter=Q(**{query_prefix + "resfactors__included_in_final_model": True}),
            ),
            "adjustment_factors_considered": str_m2m(
                query_prefix + "resfactors__adjustment_factor__description",
                filter=Q(**{query_prefix + "resfactors__included_in_final_model": False}),
            ),
            "statistical_power_display": sql_display(
                query_prefix + "statistical_power", constants.StatisticalPower
            ),
            "estimate_type_display": sql_display(
                query_prefix + "estimate_type", constants.EstimateType
            ),
            "variance_type_display": sql_display(
                query_prefix + "variance_type", constants.VarianceType
            ),
        }


class GroupExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "group_id": "group_id",
            "name": "name",
            "numeric": "numeric",
            "comparative_name": "comparative_name",
            "sex": "sex_display",
            "ethnicities": "ethnicities",
            "eligible_n": "eligible_n",
            "invited_n": "invited_n",
            "participant_n": "participant_n",
            "isControl": "isControl",
            "comments": "comments",
            "created": "created",
            "last_updated": "last_updated",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "sex_display": sql_display(query_prefix + "sex", constants.Sex),
            "ethnicities": str_m2m(query_prefix + "ethnicities__name"),
        }


class GroupResultExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "n": "n",
            "estimate": "estimate",
            "variance": "variance",
            "lower_ci": "lower_ci",
            "upper_ci": "upper_ci",
            "lower_range": "lower_range",
            "upper_range": "upper_range",
            "lower_bound_interval": "lower_bound_interval",
            "upper_bound_interval": "upper_bound_interval",
            "p_value_qualifier": "p_value_qualifier_display",
            "p_value": "p_value",
            "is_main_finding": "is_main_finding",
            "main_finding_support": "main_finding_support_display",
            "created": "created",
            "last_updated": "last_updated",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "lower_bound_interval": Case(
                When(**{query_prefix + "lower_ci": None}, then=query_prefix + "lower_range"),
                default=query_prefix + "lower_ci",
            ),
            "upper_bound_interval": Case(
                When(**{query_prefix + "upper_ci": None}, then=query_prefix + "upper_range"),
                default=query_prefix + "upper_ci",
            ),
            "p_value_qualifier_display": sql_display(
                query_prefix + "p_value_qualifier", constants.PValueQualifier
            ),
            "main_finding_support_display": sql_display(
                query_prefix + "main_finding_support", constants.MainFinding
            ),
        }


class EpiExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport("study", "study_population__study"),
            StudyPopulationExport("sp", "study_population"),
            OutcomeExport("outcome", ""),
            ExposureExport("exposure", "results__comparison_set__exposure"),
            ComparisonSetExport("cs", "results__comparison_set"),
            ResultMetricExport("metric", "results__metric"),
            ResultExport("result", "results"),
            GroupExport("group", "results__results__group"),
            GroupResultExport("result_group", "results__results"),
        ]


class OutcomeComplete(FlatFileExporter):
    """
    Returns a complete export of all data required to rebuild the the
    epidemiological meta-result study type from scratch.
    """

    def build_df(self) -> pd.DataFrame:
        return EpiExporter().get_df(self.queryset)


class OutcomeDataPivot(FlatFileExporter):
    def _get_header_row(self):
        if self.queryset.first() is None:
            self.rob_headers, self.rob_data = {}, {}
        else:
            outcome_ids = set(self.queryset.values_list("id", flat=True))
            self.rob_headers, self.rob_data = FinalRiskOfBiasScore.get_dp_export(
                self.queryset.first().assessment_id,
                outcome_ids,
                "epi",
            )

        headers = [
            "study id",
            "study name",
            "study identifier",
            "study published",
            "study population id",
            "study population name",
            "study population age profile",
            "study population source",
            "design",
            "outcome id",
            "outcome name",
            "outcome system",
            "outcome effect",
            "outcome effect subtype",
            "diagnostic",
            "age of outcome measurement",
            "tags",
        ]

        headers.extend(list(self.rob_headers.values()))

        headers.extend(
            [
                "comparison set id",
                "comparison set name",
                "exposure id",
                "exposure name",
                "exposure metric",
                "exposure measured",
                "dose units",
                "age of exposure",
                "exposure estimate",
                "exposure estimate type",
                "exposure variance",
                "exposure variance type",
                "exposure lower bound interval",
                "exposure upper bound interval",
                "exposure lower ci",
                "exposure upper ci",
                "exposure lower range",
                "exposure upper range",
                "result id",
                "result name",
                "result population description",
                "result tags",
                "statistical metric",
                "statistical metric abbreviation",
                "statistical metric description",
                "result summary",
                "dose response",
                "statistical power",
                "statistical test results",
                "CI units",
                "exposure group order",
                "exposure group name",
                "exposure group comparison name",
                "exposure group numeric",
                "Reference/Exposure group",
                "Result, summary numerical",
                "key",
                "result group id",
                "N",
                "estimate",
                "lower CI",
                "upper CI",
                "lower range",
                "upper range",
                "lower bound interval",
                "upper bound interval",
                "variance",
                "statistical significance",
                "statistical significance (numeric)",
                "main finding",
                "main finding support",
                "percent control mean",
                "percent control low",
                "percent control high",
            ]
        )

        return headers

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = [
                ser["study_population"]["study"]["id"],
                ser["study_population"]["study"]["short_citation"],
                ser["study_population"]["study"]["study_identifier"],
                ser["study_population"]["study"]["published"],
                ser["study_population"]["id"],
                ser["study_population"]["name"],
                ser["study_population"]["age_profile"],
                ser["study_population"]["source"],
                ser["study_population"]["design"],
                ser["id"],
                ser["name"],
                ser["system"],
                ser["effect"],
                ser["effect_subtype"],
                ser["diagnostic"],
                ser["age_of_measurement"],
                self.get_flattened_tags(ser, "effects"),
            ]
            outcome_robs = [
                self.rob_data[(ser["id"], metric_id)] for metric_id in self.rob_headers.keys()
            ]
            row.extend(outcome_robs)

            for res in ser["results"]:
                row_copy = list(row)

                # comparison set
                row_copy.extend([res["comparison_set"]["id"], res["comparison_set"]["name"]])

                # exposure (may be missing)
                if res["comparison_set"]["exposure"]:
                    row_copy.extend(
                        [
                            res["comparison_set"]["exposure"]["id"],
                            res["comparison_set"]["exposure"]["name"],
                            res["comparison_set"]["exposure"]["metric"],
                            res["comparison_set"]["exposure"]["measured"],
                            res["comparison_set"]["exposure"]["metric_units"]["name"],
                            res["comparison_set"]["exposure"]["age_of_exposure"],
                        ]
                    )

                    num_rows_for_ct = len(res["comparison_set"]["exposure"]["central_tendencies"])
                    if num_rows_for_ct == 0:
                        row_copy.extend(["-"] * 10)
                        self.addOutcomesAndGroupsToRowAndAppend(rows, res, ser, row_copy)
                    else:
                        for ct in res["comparison_set"]["exposure"]["central_tendencies"]:
                            row_copy_ct = list(row_copy)
                            row_copy_ct.extend(
                                [
                                    ct["estimate"],
                                    ct["estimate_type"],
                                    ct["variance"],
                                    ct["variance_type"],
                                    ct["lower_bound_interval"],
                                    ct["upper_bound_interval"],
                                    ct["lower_ci"],
                                    ct["upper_ci"],
                                    ct["lower_range"],
                                    ct["upper_range"],
                                ]
                            )
                            self.addOutcomesAndGroupsToRowAndAppend(rows, res, ser, row_copy_ct)

                else:
                    row_copy.extend(["-"] * (6 + 10))  # exposure + exposure.central_tendencies
                    self.addOutcomesAndGroupsToRowAndAppend(rows, res, ser, row_copy)

        return rows

    def addOutcomesAndGroupsToRowAndAppend(self, rows, res, ser, row):
        # outcome details
        row.extend(
            [
                res["id"],
                res["name"],
                res["population_description"],
                self.get_flattened_tags(res, "resulttags"),
                res["metric"]["metric"],
                res["metric"]["abbreviation"],
                res["metric_description"],
                res["comments"],
                res["dose_response"],
                res["statistical_power"],
                res["statistical_test_results"],
                res["ci_units"],
            ]
        )

        for rg in res["results"]:
            row_copy = list(row)
            row_copy.extend(
                [
                    rg["group"]["group_id"],
                    rg["group"]["name"],
                    rg["group"]["comparative_name"],
                    rg["group"]["numeric"],
                    f'{ser["study_population"]["study"]["short_citation"]} ({rg["group"]["name"]}, n={rg["n"]})',
                    f'{rg["estimate"]} ({rg["lower_ci"]} - {rg["upper_ci"]})',
                    rg["id"],
                    rg["id"],  # repeat for data-pivot key
                    rg["n"],
                    rg["estimate"],
                    rg["lower_ci"],
                    rg["upper_ci"],
                    rg["lower_range"],
                    rg["upper_range"],
                    rg["lower_bound_interval"],
                    rg["upper_bound_interval"],
                    rg["variance"],
                    rg["p_value_text"],
                    rg["p_value"],
                    rg["is_main_finding"],
                    rg["main_finding_support"],
                    rg["percentControlMean"],
                    rg["percentControlLow"],
                    rg["percentControlHigh"],
                ]
            )
            rows.append(row_copy)
