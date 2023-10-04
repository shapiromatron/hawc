import math

import pandas as pd
from django.db.models import Case, Q, When

from ..common.exports import Exporter, ModelExport
from ..common.helper import FlatFileExporter
from ..common.models import sql_display, sql_format, str_m2m
from ..materialized.models import FinalRiskOfBiasScore
from ..study.exports import StudyExport
from . import constants, models


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
        return self.format_time(df)


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

    def prepare_df(self, df):
        return self.format_time(df)


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

    def prepare_df(self, df):
        return self.format_time(df)


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

    def prepare_df(self, df):
        return self.format_time(df)


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
            "tags": "tags",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "dose_response_display": sql_display(
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
            "tags": str_m2m(query_prefix + "resulttags__name"),
        }

    def prepare_df(self, df):
        return self.format_time(df)


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

    def prepare_df(self, df):
        return self.format_time(df)


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

    def prepare_df(self, df):
        return self.format_time(df)


class CentralTendencyExport(ModelExport):
    def get_value_map(self):
        return {
            "estimate": "estimate",
            "estimate_type": "estimate_type_display",
            "variance": "variance",
            "variance_type": "variance_type_display",
            "lower_bound_interval": "lower_bound_interval",
            "upper_bound_interval": "upper_bound_interval",
            "lower_ci": "lower_ci",
            "upper_ci": "upper_ci",
            "lower_range": "lower_range",
            "upper_range": "upper_range",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "estimate_type_display": sql_display(
                query_prefix + "estimate_type", constants.EstimateType
            ),
            "variance_type_display": sql_display(
                query_prefix + "variance_type", constants.VarianceType
            ),
            "lower_bound_interval": Case(
                When(**{query_prefix + "lower_ci": None}, then=query_prefix + "lower_range"),
                default=query_prefix + "lower_ci",
            ),
            "upper_bound_interval": Case(
                When(**{query_prefix + "upper_ci": None}, then=query_prefix + "upper_range"),
                default=query_prefix + "upper_ci",
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
            ResultExport("result", "results", exclude=("tags",)),
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


class EpiDataPivotExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport(
                "study",
                "study_population__study",
                include=("id", "short_citation", "study_identifier", "published"),
            ),
            StudyPopulationExport(
                "sp", "study_population", include=("id", "name", "age_profile", "source", "design")
            ),
            OutcomeExport(
                "outcome",
                "",
                include=(
                    "id",
                    "name",
                    "system",
                    "effect",
                    "effect_subtype",
                    "diagnostic",
                    "age_of_measurement",
                    "effects",
                ),
            ),
            ComparisonSetExport("cs", "results__comparison_set", include=("id", "name")),
            ExposureExport(
                "exposure",
                "results__comparison_set__exposure",
                include=(
                    "id",
                    "name",
                    "metric",
                    "measured",
                    "metric_units_name",
                    "age_of_exposure",
                ),
            ),
            CentralTendencyExport(
                "ct",
                "results__comparison_set__exposure__central_tendencies",
                include=(
                    "estimate",
                    "estimate_type",
                    "variance",
                    "variance_type",
                    "lower_bound_interval",
                    "upper_bound_interval",
                    "lower_ci",
                    "upper_ci",
                    "lower_range",
                    "upper_range",
                ),
            ),
            ResultExport(
                "result",
                "results",
                include=(
                    "id",
                    "name",
                    "population_description",
                    "tags",
                    "metric_description",
                    "comments",
                    "dose_response",
                    "statistical_power",
                    "statistical_test_results",
                    "ci_units",
                    "estimate_type",
                    "variance_type",
                ),
            ),
            ResultMetricExport("metric", "results__metric", include=("name", "abbreviation")),
            GroupExport(
                "group",
                "results__results__group",
                include=("group_id", "name", "comparative_name", "numeric", "isControl"),
            ),
            GroupResultExport(
                "result_group",
                "results__results",
                include=(
                    "id",
                    "n",
                    "estimate",
                    "lower_ci",
                    "upper_ci",
                    "lower_range",
                    "upper_range",
                    "lower_bound_interval",
                    "upper_bound_interval",
                    "variance",
                    "p_value",
                    "p_value_qualifier",
                    "is_main_finding",
                    "main_finding_support",
                ),
            ),
        ]


def percent_control(n_1, mu_1, sd_1, n_2, mu_2, sd_2):
    mean = low = high = None

    if mu_1 and mu_2 and mu_1 != 0:
        mean = (mu_2 - mu_1) / mu_1 * 100.0
        if sd_1 and sd_2 and n_1 and n_2:
            sd = math.sqrt(
                pow(mu_1, -2)
                * ((pow(sd_2, 2) / n_2) + (pow(mu_2, 2) * pow(sd_1, 2)) / (n_1 * pow(mu_1, 2)))
            )
            ci = (1.96 * sd) * 100
            rng = sorted([mean - ci, mean + ci])
            low = rng[0]
            high = rng[1]

    return mean, low, high


class OutcomeDataPivot(FlatFileExporter):
    def _add_percent_control(self, df: pd.DataFrame) -> pd.DataFrame:
        def _get_stdev(x: pd.Series):
            return models.GroupResult.stdev(
                x["result-variance_type"], x["result_group-variance"], x["result_group-n"]
            )

        def _apply_results(_df1: pd.DataFrame):
            controls = _df1.loc[_df1["group-isControl"] is True]
            control = _df1.iloc[0] if controls.empty else controls.iloc[0]
            n_1 = control["result_group-n"]
            mu_1 = control["result_group-estimate"]
            sd_1 = _get_stdev(control)

            def _apply_result_groups(_df2: pd.DataFrame):
                row = _df2.iloc[0]
                if control["result-estimate_type"] in ["median", "mean"] and control[
                    "result-variance_type"
                ] in [
                    "SD",
                    "SE",
                    "SEM",
                ]:
                    n_2 = row["result_group-n"]
                    mu_2 = row["result_group-estimate"]
                    sd_2 = _get_stdev(row)
                    mean, low, high = percent_control(n_1, mu_1, sd_1, n_2, mu_2, sd_2)
                    return pd.DataFrame(
                        [[mean, low, high]],
                        columns=[
                            "percent control mean",
                            "percent control low",
                            "percent control high",
                        ],
                        index=[row["result_group-id"]],
                    )
                return pd.DataFrame(
                    [],
                    columns=[
                        "percent control mean",
                        "percent control low",
                        "percent control high",
                    ],
                )

            rgs = _df1.groupby("result_group-id", group_keys=False)
            return rgs.apply(_apply_result_groups)

        results = df.groupby("result-id", group_keys=False)
        computed_df = results.apply(_apply_results)
        return df.join(computed_df, on="result_group-id").drop(
            columns=["result-estimate_type", "result-variance_type", "group-isControl"]
        )

    def build_df(self) -> pd.DataFrame:
        df = EpiDataPivotExporter().get_df(self.queryset.order_by("id", "results__results"))
        outcome_ids = list(df["outcome-id"].unique())
        rob_headers, rob_data = FinalRiskOfBiasScore.get_dp_export(
            self.queryset.first().assessment_id,
            outcome_ids,
            "epi",
        )
        rob_df = pd.DataFrame(
            data=[
                [rob_data[(outcome_id, metric_id)] for metric_id in rob_headers.keys()]
                for outcome_id in outcome_ids
            ],
            columns=list(rob_headers.values()),
            index=outcome_ids,
        )
        df = df.join(rob_df, on="outcome-id")

        df["Reference/Exposure group"] = (
            df["study-short_citation"]
            + " ("
            + df["group-name"]
            + ", n="
            + df["result_group-n"].astype(str)
            + ")"
        )
        df["Result, summary numerical"] = (
            df["result_group-estimate"].astype(str)
            + " ("
            + df["result_group-lower_ci"].astype(str)
            + " - "
            + df["result_group-upper_ci"].astype(str)
            + ")"
        )
        df["key"] = df["result_group-id"]
        df["statistical significance"] = df.apply(
            lambda x: x["result_group-p_value_qualifier"]
            if pd.isna(x["result_group-p_value"])
            else f"{x['result_group-p_value']:g}"
            if x["result_group-p_value_qualifier"] in ["=", "-", "n.s."]
            else f"{x['result_group-p_value_qualifier']}{x['result_group-p_value']:g}",
            axis="columns",
        )
        df = df.drop(columns="result_group-p_value_qualifier")

        df = self._add_percent_control(df)

        df = df.rename(
            columns={
                "study-id": "study id",
                "study-short_citation": "study name",
                "study-study_identifier": "study identifier",
                "study-published": "study published",
                "sp-id": "study population id",
                "sp-name": "study population name",
                "sp-age_profile": "study population age profile",
                "sp-source": "study population source",
                "sp-design": "design",
                "outcome-id": "outcome id",
                "outcome-name": "outcome name",
                "outcome-system": "outcome system",
                "outcome-effect": "outcome effect",
                "outcome-effect_subtype": "outcome effect subtype",
                "outcome-diagnostic": "diagnostic",
                "outcome-age_of_measurement": "age of outcome measurement",
                "outcome-effects": "tags",
            },
            errors="raise",
        )
        df = df.rename(
            columns={
                "cs-id": "comparison set id",
                "cs-name": "comparison set name",
                "exposure-id": "exposure id",
                "exposure-name": "exposure name",
                "exposure-metric": "exposure metric",
                "exposure-measured": "exposure measured",
                "exposure-metric_units_name": "dose units",
                "exposure-age_of_exposure": "age of exposure",
                "ct-estimate": "exposure estimate",
                "ct-estimate_type": "exposure estimate type",
                "ct-variance": "exposure variance",
                "ct-variance_type": "exposure variance type",
                "ct-lower_bound_interval": "exposure lower bound interval",
                "ct-upper_bound_interval": "exposure upper bound interval",
                "ct-lower_ci": "exposure lower ci",
                "ct-upper_ci": "exposure upper ci",
                "ct-lower_range": "exposure lower range",
                "ct-upper_range": "exposure upper range",
                "result-id": "result id",
                "result-name": "result name",
                "result-population_description": "result population description",
                "result-tags": "result tags",
                "metric-name": "statistical metric",
                "metric-abbreviation": "statistical metric abbreviation",
                "result-metric_description": "statistical metric description",
                "result-comments": "result summary",
                "result-dose_response": "dose response",
                "result-statistical_power": "statistical power",
                "result-statistical_test_results": "statistical test results",
                "result-ci_units": "CI units",
                "group-group_id": "exposure group order",
                "group-name": "exposure group name",
                "group-comparative_name": "exposure group comparison name",
                "group-numeric": "exposure group numeric",
                # "Reference/Exposure group", # format string
                # "Result, summary numerical", # format string
                # "key", # copy of result_group-id
                "result_group-id": "result group id",
                "result_group-n": "N",
                "result_group-estimate": "estimate",
                "result_group-lower_ci": "lower CI",
                "result_group-upper_ci": "upper CI",
                "result_group-lower_range": "lower range",
                "result_group-upper_range": "upper range",
                "result_group-lower_bound_interval": "lower bound interval",
                "result_group-upper_bound_interval": "upper bound interval",
                "result_group-variance": "variance",
                # "result_group-p_value_text":"statistical significance", # add this; its computed
                "result_group-p_value": "statistical significance (numeric)",
                "result_group-is_main_finding": "main finding",
                "result_group-main_finding_support": "main finding support",
                # "percent control mean", # some function
                # "percent control low", # some function
                # "percent control high", # some function
            },
            errors="raise",
        )

        return df


class OutcomeDataPivot2(FlatFileExporter):
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
