import math
from collections import defaultdict

import numpy as np
import pandas as pd
from django.db.models import CharField, F
from django.db.models.functions import Cast
from django.db.models.lookups import Exact
from scipy import stats

from ..assessment.models import DoseUnits
from ..bmd.models import Session
from ..common.exports import Exporter, ModelExport
from ..common.helper import FlatFileExporter, cleanHTML
from ..common.models import sql_display, sql_format, str_m2m
from ..materialized.exports import get_final_score_df
from ..study.exports import StudyExport
from ..udf.exports import ModelUDFContentExport
from . import constants, models


def cont_ci(stdev, n, response):
    """
    Two-tailed t-test, assuming 95% confidence interval.
    """
    se = stdev / math.sqrt(n)
    change = stats.t.ppf(0.975, max(n - 1, 1)) * se
    lower_ci = response - change
    upper_ci = response + change
    return lower_ci, upper_ci


def dich_ci(incidence, n):
    """
    Add confidence intervals to dichotomous datasets.
    https://www.epa.gov/sites/production/files/2020-09/documents/bmds_3.2_user_guide.pdf

    The error bars shown in BMDS plots use alpha = 0.05 and so
    represent the 95% confidence intervals on the observed
    proportions (independent of model).
    """
    p = incidence / float(n)
    z = stats.norm.ppf(1 - 0.05 / 2)
    z2 = z * z
    q = 1.0 - p
    tmp1 = 2 * n * p + z2
    lower_ci = ((tmp1 - 1) - z * np.sqrt(z2 - (2 + 1 / n) + 4 * p * (n * q + 1))) / (2 * (n + z2))
    upper_ci = ((tmp1 + 1) + z * np.sqrt(z2 + (2 + 1 / n) + 4 * p * (n * q - 1))) / (2 * (n + z2))
    return lower_ci, upper_ci


def percent_control(n_1, mu_1, sd_1, n_2, mu_2, sd_2):
    mean = low = high = None

    if mu_1 is not None and mu_2 is not None and mu_1 > 0 and mu_2 > 0:
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


def maximum_percent_control_change(changes: list):
    """
    For each endpoint, return the maximum absolute-change percent control
    for that endpoint, or 0 if it cannot be calculated. Useful for
    ordering data-pivot results.
    """
    val = 0

    if len(changes) > 0:
        min_ = min(changes)
        max_ = max(changes)
        val = min_ if abs(min_) > abs(max_) else max_

    return val


class ExperimentExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "url": "url",
            "name": "name",
            "type_display": "type_display",
            "has_multiple_generations": "has_multiple_generations",
            "chemical": "chemical",
            "cas": "cas",
            "dtxsid": "dtxsid",
            "chemical_source": "chemical_source",
            "purity_available": "purity_available",
            "purity_qualifier": "purity_qualifier",
            "purity": "purity",
            "vehicle": "vehicle",
            "guideline_compliance": "guideline_compliance",
            "description": "description",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "url": sql_format("/ani/experiment/{}/", query_prefix + "id"),  # hardcoded URL
            "type_display": sql_display(query_prefix + "type", constants.ExperimentType),
        }

    def prepare_df(self, df):
        # clean html text
        description = self.get_column_name("description")
        if description in df.columns:
            df.loc[:, description] = df[description].apply(cleanHTML)
        return df


class AnimalGroupExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "url": "url",
            "name": "name",
            "sex_display": "sex_display",
            "sex_symbol": "sex_symbol",
            "animal_source": "animal_source",
            "lifestage_exposed": "lifestage_exposed",
            "lifestage_assessed": "lifestage_assessed",
            "siblings": "siblings",
            "parents_display": "parents_display",
            "generation": "generation",
            "comments": "comments",
            "diet": "diet",
            "species_name": "species__name",
            "strain_name": "strain__name",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "url": sql_format("/ani/animal-group/{}/", query_prefix + "id"),  # hardcoded URL
            "sex_display": sql_display(query_prefix + "sex", constants.Sex),
            "sex_symbol": sql_display(query_prefix + "sex", models.AnimalGroup.SEX_SYMBOLS),
            "parents_display": str_m2m(Cast(query_prefix + "parents", output_field=CharField())),
        }

    def prepare_df(self, df):
        # clean html text
        comments = self.get_column_name("comments")
        if comments in df.columns:
            df.loc[:, comments] = df[comments].apply(cleanHTML)
        return df


class DosingRegimeExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "dosed_animals": "dosed_animals",
            "route_of_exposure_display": "route_of_exposure_display",
            "duration_exposure": "duration_exposure",
            "duration_exposure_text": "duration_exposure_text",
            "duration_observation": "duration_observation",
            "num_dose_groups": "num_dose_groups",
            "positive_control_display": "positive_control_display",
            "negative_control_display": "negative_control_display",
            "description": "description",
        }

    def get_annotation_map(self, query_prefix):
        POSITIVE_CONTROL = {k: v for k, v in constants.POSITIVE_CONTROL_CHOICES}
        return {
            "route_of_exposure_display": sql_display(
                query_prefix + "route_of_exposure", constants.RouteExposure
            ),
            "positive_control_display": sql_display(
                query_prefix + "positive_control", POSITIVE_CONTROL
            ),
            "negative_control_display": sql_display(
                query_prefix + "negative_control", constants.NegativeControl
            ),
        }

    def prepare_df(self, df):
        # clean html text
        description = self.get_column_name("description")
        if description in df.columns:
            df.loc[:, description] = df[description].apply(cleanHTML)
        return df


class EndpointExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "url": "url",
            "name": "name",
            "effects_display": "effects_display",
            "system": "system",
            "organ": "organ",
            "effect": "effect",
            "effect_subtype": "effect_subtype",
            "name_term_id": "name_term_id",
            "system_term_id": "system_term_id",
            "organ_term_id": "organ_term_id",
            "effect_term_id": "effect_term_id",
            "effect_subtype_term_id": "effect_subtype_term_id",
            "litter_effects": "litter_effects",
            "litter_effect_notes": "litter_effect_notes",
            "observation_time": "observation_time",
            "observation_time_units_display": "observation_time_units_display",
            "observation_time_text": "observation_time_text",
            "data_location": "data_location",
            "response_units": "response_units",
            "data_type": "data_type",
            "data_type_display": "data_type_display",
            "variance_type": "variance_type",
            "variance_type_name": "variance_type_name",
            "confidence_interval": "confidence_interval",
            "data_reported": "data_reported",
            "data_extracted": "data_extracted",
            "values_estimated": "values_estimated",
            "expected_adversity_direction": "expected_adversity_direction",
            "expected_adversity_direction_display": "expected_adversity_direction_display",
            "monotonicity_display": "monotonicity_display",
            "statistical_test": "statistical_test",
            "trend_value": "trend_value",
            "trend_result_display": "trend_result_display",
            "diagnostic": "diagnostic",
            "power_notes": "power_notes",
            "results_notes": "results_notes",
            "endpoint_notes": "endpoint_notes",
            "additional_fields": "additional_fields",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "url": sql_format("/ani/endpoint/{}/", query_prefix + "id"),  # hardcoded URL
            "effects_display": str_m2m(query_prefix + "effects__name"),
            "observation_time_units_display": sql_display(
                query_prefix + "observation_time_units", constants.ObservationTimeUnits
            ),
            "data_type_display": sql_display(query_prefix + "data_type", constants.DataType),
            "variance_type_name": sql_display(
                query_prefix + "variance_type", models.Endpoint.VARIANCE_NAME
            ),
            "expected_adversity_direction_display": sql_display(
                query_prefix + "expected_adversity_direction", constants.AdverseDirection
            ),
            "monotonicity_display": sql_display(
                query_prefix + "monotonicity", constants.Monotonicity
            ),
            "trend_result_display": sql_display(
                query_prefix + "trend_result", constants.TrendResult
            ),
        }

    def prepare_df(self, df):
        # clean html text
        results_notes = self.get_column_name("results_notes")
        if results_notes in df.columns:
            df.loc[:, results_notes] = df[results_notes].apply(cleanHTML)

        endpoint_notes = self.get_column_name("endpoint_notes")
        if results_notes in df.columns:
            df.loc[:, endpoint_notes] = df[endpoint_notes].apply(cleanHTML)

        return df


class EndpointGroupExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "dose_group_id": "dose_group_id",
            "n": "n",
            "incidence": "incidence",
            "response": "response",
            "variance": "variance",
            "lower_ci": "lower_ci",
            "upper_ci": "upper_ci",
            "significant": "significant",
            "significance_level": "significance_level",
            "treatment_effect": "treatment_effect",
            "treatment_effect_display": "treatment_effect_display",
            "NOEL": "NOEL",
            "LOEL": "LOEL",
            "FEL": "FEL",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "treatment_effect_display": sql_display(
                query_prefix + "treatment_effect", constants.TreatmentEffect, default=None
            ),
            "NOEL": Exact(F(query_prefix + "dose_group_id"), F(query_prefix + "endpoint__NOEL")),
            "LOEL": Exact(F(query_prefix + "dose_group_id"), F(query_prefix + "endpoint__LOEL")),
            "FEL": Exact(F(query_prefix + "dose_group_id"), F(query_prefix + "endpoint__FEL")),
        }


class DoseGroupExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "dose_units_id": "dose_units__id",
            "dose_units_name": "dose_units__name",
            "dose_group_id": "dose_group_id",
            "dose": "dose",
        }


class EndpointGroupFlatCompleteExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport(
                "study",
                "animal_group__experiment__study",
            ),
            ExperimentExport(
                "experiment",
                "animal_group__experiment",
            ),
            AnimalGroupExport("animal_group", "animal_group", exclude=("sex_symbol",)),
            DosingRegimeExport(
                "dosing_regime",
                "animal_group__dosing_regime",
            ),
            EndpointExport(
                "endpoint", "", exclude=("expected_adversity_direction", "data_type_display")
            ),
            EndpointGroupExport("endpoint_group", "groups", exclude=("treatment_effect",)),
            DoseGroupExport(
                "dose_group", "animal_group__dosing_regime__doses", exclude=("dose_units_id",)
            ),
        ]


class EndpointGroupFlatComplete(FlatFileExporter):
    def handle_doses(self, df: pd.DataFrame) -> pd.DataFrame:
        # TODO this is really slow; maybe its the filtering to find matching dose group ids?
        # solutions: ?, put the burden on SQL w/ Prefetch and Subquery (messy)
        # long term solutions: group and dose group should be related
        def _func(group_df: pd.DataFrame) -> pd.DataFrame:
            # handle case with no dose data
            if group_df["dose_group-id"].isna().all():
                return group_df

            # add dose data
            group_df["doses-" + group_df["dose_group-dose_units_name"]] = group_df[
                "dose_group-dose"
            ].tolist()

            # return a df that is dose agnostic
            return group_df.drop_duplicates(
                subset=group_df.columns[group_df.columns.str.endswith("-id")].difference(
                    ["dose_group-id"]
                )
            )

        return (
            df.groupby("endpoint_group-id", group_keys=False, sort=False)
            .apply(_func)
            .drop(
                columns=[
                    "dose_group-id",
                    "dose_group-dose_units_name",
                    "dose_group-dose_group_id",
                    "dose_group-dose",
                ]
            )
            .reset_index(drop=True)
        )

    def handle_stdev(self, df: pd.DataFrame) -> pd.DataFrame:
        df["endpoint_group-stdev"] = df.apply(
            lambda x: models.EndpointGroup.stdev(
                x["endpoint-variance_type"],
                x["endpoint_group-variance"],
                x["endpoint_group-n"],
            ),
            axis="columns",
        )
        return df.drop(columns=["endpoint-variance_type"])

    def handle_ci(self, df: pd.DataFrame) -> pd.DataFrame:
        def _func(row: pd.Series) -> pd.Series:
            # logic used from EndpointGroup.getConfidenceIntervals()
            data_type = row["endpoint-data_type"]
            lower_ci = row["endpoint_group-lower_ci"]
            upper_ci = row["endpoint_group-upper_ci"]
            n = row["endpoint_group-n"]

            response = row["endpoint_group-response"]
            stdev = row["endpoint_group-stdev"]
            incidence = row["endpoint_group-incidence"]
            if lower_ci is not None or upper_ci is not None or n is None or n <= 0:
                pass
            elif (
                data_type == constants.DataType.CONTINUOUS
                and response is not None
                and stdev is not None
            ):
                (
                    row["endpoint_group-lower_ci"],
                    row["endpoint_group-upper_ci"],
                ) = cont_ci(stdev, n, response)
            elif (
                data_type in [constants.DataType.DICHOTOMOUS, constants.DataType.DICHOTOMOUS_CANCER]
                and incidence is not None
            ):
                (
                    row["endpoint_group-lower_ci"],
                    row["endpoint_group-upper_ci"],
                ) = dich_ci(incidence, n)
            return row

        return df.apply(_func, axis="columns").drop(columns=["endpoint_group-stdev"])

    def build_df(self) -> pd.DataFrame:
        df = EndpointGroupFlatCompleteExporter().get_df(
            self.queryset.select_related(
                "animal_group__experiment__study",
                "animal_group__dosing_regime",
            )
            .prefetch_related("groups", "animal_group__dosing_regime__doses")
            .order_by("id", "groups", "animal_group__dosing_regime__doses")
        )
        df = df[
            pd.isna(df["dose_group-id"])
            | (df["endpoint_group-dose_group_id"] == df["dose_group-dose_group_id"])
        ]
        if df.empty:
            return df
        if obj := self.queryset.first():
            doses = DoseUnits.objects.get_animal_units_names(obj.assessment_id)

            df = df.assign(**{f"doses-{d}": None for d in doses})
            df = self.handle_doses(df)
        df["dosing_regime-dosed_animals"] = df["dosing_regime-dosed_animals"].astype(str)
        df = self.handle_stdev(df)
        df = self.handle_ci(df)

        df = df.rename(
            columns={
                "endpoint_group-treatment_effect_display": "endpoint_group-treatment_effect",
                "endpoint-expected_adversity_direction_display": "endpoint-expected_adversity_direction",
                "experiment-type_display": "experiment-type",
                "animal_group-sex_display": "animal_group-sex",
                "dosing_regime-positive_control_display": "dosing_regime-positive_control",
                "endpoint-effects_display": "endpoint-effects",
                "animal_group-parents_display": "animal_group-parents",
                "dosing_regime-route_of_exposure_display": "dosing_regime-route_of_exposure",
                "endpoint-monotonicity_display": "endpoint-monotonicity",
                "dosing_regime-negative_control_display": "dosing_regime-negative_control",
                "endpoint-observation_time_units_display": "endpoint-observation_time_units",
                "endpoint-trend_result_display": "endpoint-trend_result",
                "endpoint-variance_type_name": "endpoint-variance_type",
                "animal_group-species_name": "species-name",
                "animal_group-strain_name": "strain-name",
            }
        )

        return df


class EndpointGroupFlatDataPivotExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport(
                "study",
                "animal_group__experiment__study",
                include=("id", "short_citation", "study_identifier", "published"),
            ),
            ModelUDFContentExport(
                "study_udf_content",
                "animal_group__experiment__study__udf_content",
                include=("content",),
            ),
            ExperimentExport(
                "experiment",
                "animal_group__experiment",
                include=("id", "name", "type_display", "chemical"),
            ),
            AnimalGroupExport(
                "animal_group",
                "animal_group",
                include=(
                    "id",
                    "name",
                    "lifestage_exposed",
                    "lifestage_assessed",
                    "species_name",
                    "strain_name",
                    "generation",
                    "sex_display",
                    "sex_symbol",
                ),
            ),
            ModelUDFContentExport(
                "animal_group_udf_content",
                "animal_group__udf_content",
                include=("content",),
            ),
            DosingRegimeExport(
                "dosing_regime",
                "animal_group__dosing_regime",
                include=(
                    "route_of_exposure_display",
                    "duration_exposure_text",
                    "duration_exposure",
                ),
            ),
            EndpointExport(
                "endpoint",
                "",
                include=(
                    "id",
                    "name",
                    "system",
                    "organ",
                    "effect",
                    "effect_subtype",
                    "diagnostic",
                    "effects_display",
                    "observation_time",
                    "observation_time_units_display",
                    "observation_time_text",
                    "variance_type",
                    "data_type",
                    "data_type_display",
                    "trend_value",
                    "trend_result_display",
                    "expected_adversity_direction",
                    "response_units",
                ),
            ),
            ModelUDFContentExport(
                "endpoint_udf_content",
                "udf_content",
                include=("content",),
            ),
            EndpointGroupExport(
                "endpoint_group",
                "groups",
                include=(
                    "id",
                    "dose_group_id",
                    "n",
                    "incidence",
                    "response",
                    "lower_ci",
                    "upper_ci",
                    "significant",
                    "significance_level",
                    "treatment_effect_display",
                    "NOEL",
                    "LOEL",
                    "FEL",
                    "variance",
                ),
            ),
            DoseGroupExport(
                "dose_group",
                "animal_group__dosing_regime__doses",
                include=("id", "dose_units_id", "dose_units_name", "dose_group_id", "dose"),
            ),
        ]


class EndpointGroupFlatDataPivot(FlatFileExporter):
    def get_preferred_units(self, df: pd.DataFrame) -> int | None:
        preferred_units = self.kwargs.get("preferred_units", None)
        available_units = df["dose_group-dose_units_id"].dropna().unique()
        if available_units.size == 0:
            return None
        if preferred_units:
            for units in preferred_units:
                if units in available_units:
                    return units
        return available_units[0]

    def handle_ci(self, df: pd.DataFrame) -> pd.DataFrame:
        def _func(row: pd.Series) -> pd.Series:
            # logic used from EndpointGroup.getConfidenceIntervals()
            data_type = row["endpoint-data_type"]
            lower_ci = row["endpoint_group-lower_ci"]
            upper_ci = row["endpoint_group-upper_ci"]
            n = row["endpoint_group-n"]

            response = row["endpoint_group-response"]
            stdev = row["endpoint_group-stdev"]
            incidence = row["endpoint_group-incidence"]
            if lower_ci is not None or upper_ci is not None or n is None or n <= 0:
                pass
            elif (
                data_type == constants.DataType.CONTINUOUS
                and response is not None
                and stdev is not None
            ):
                (
                    row["endpoint_group-lower_ci"],
                    row["endpoint_group-upper_ci"],
                ) = cont_ci(stdev, n, response)
            elif (
                data_type in [constants.DataType.DICHOTOMOUS, constants.DataType.DICHOTOMOUS_CANCER]
                and incidence is not None
            ):
                (
                    row["endpoint_group-lower_ci"],
                    row["endpoint_group-upper_ci"],
                ) = dich_ci(incidence, n)
            return row

        return df.apply(_func, axis="columns")

    def handle_stdev(self, df: pd.DataFrame) -> pd.DataFrame:
        df["endpoint_group-stdev"] = df.apply(
            lambda x: models.EndpointGroup.stdev(
                x["endpoint-variance_type"],
                x["endpoint_group-variance"],
                x["endpoint_group-n"],
            ),
            axis="columns",
        )
        return df

    def handle_percent_control(self, df: pd.DataFrame) -> pd.DataFrame:
        def _func(group_df: pd.DataFrame) -> pd.DataFrame:
            control = group_df.iloc[0]

            data_type = control["endpoint-data_type"]
            i_1 = control["endpoint_group-incidence"]
            n_1 = control["endpoint_group-n"]
            mu_1 = control["endpoint_group-response"]
            sd_1 = control["endpoint_group-stdev"]

            def __func(row: pd.Series) -> pd.Series:
                # logic used from EndpointGroup.percentControl()
                row["percent control mean"] = None
                row["percent control low"] = None
                row["percent control high"] = None
                if data_type == constants.DataType.CONTINUOUS:
                    n_2 = row["endpoint_group-n"]
                    mu_2 = row["endpoint_group-response"]
                    sd_2 = row["endpoint_group-stdev"]
                    (
                        row["percent control mean"],
                        row["percent control low"],
                        row["percent control high"],
                    ) = percent_control(n_1, mu_1, sd_1, n_2, mu_2, sd_2)
                elif data_type == constants.DataType.PERCENT_DIFFERENCE:
                    row["percent control mean"] = row["endpoint_group-response"]
                    row["percent control low"] = row["endpoint_group-lower_ci"]
                    row["percent control high"] = row["endpoint_group-upper_ci"]
                elif data_type == constants.DataType.DICHOTOMOUS:
                    if i_1 and n_1:
                        i_2 = row["endpoint_group-incidence"]
                        n_2 = row["endpoint_group-n"]
                        if n_2:
                            row["percent control mean"] = (
                                ((i_2 / n_2) - (i_1 / n_1)) / (i_1 / n_1) * 100
                            )
                return row

            group_df = group_df.apply(__func, axis="columns")
            group_df["maximum endpoint change"] = maximum_percent_control_change(
                group_df["percent control mean"].dropna()
            )
            return group_df

        return (
            df.groupby("endpoint-id", group_keys=False, sort=False)
            .apply(_func)
            .reset_index(drop=True)
        )

    def handle_animal_description(self, df: pd.DataFrame):
        def _func(group_df: pd.DataFrame) -> pd.Series:
            gen = group_df["animal_group-generation"].iloc[0]
            if len(gen) > 0:
                gen += " "
            ns_txt = ""
            ns = group_df["endpoint_group-n"].dropna().astype(int).tolist()
            if len(ns) > 0:
                ns_txt = ", N=" + models.EndpointGroup.getNRangeText(ns)

            sex_symbol = group_df["animal_group-sex_symbol"].iloc[0]
            if sex_symbol == "NR":
                sex_symbol = "sex=NR"
            species = group_df["animal_group-species_name"].iloc[0]
            strain = group_df["animal_group-strain_name"].iloc[0]
            group_df["animal description"] = f"{gen}{species}, {strain} ({sex_symbol})"
            group_df["animal description (with N)"] = (
                f"{gen}{species}, {strain} ({sex_symbol}{ns_txt})"
            )

            return group_df

        return (
            df.groupby("endpoint-id", group_keys=False, sort=False)
            .apply(_func)
            .reset_index(drop=True)
        )

    def handle_treatment_period(self, df: pd.DataFrame) -> pd.DataFrame:
        def _calc(row):
            txt = row["experiment-type_display"].lower()
            if txt.find("(") >= 0:
                txt = txt[: txt.find("(")].strip()

            if row["dosing_regime-duration_exposure_text"]:
                txt = f"{txt} ({row['dosing_regime-duration_exposure_text']})"

            return txt

        df["treatment period"] = df.apply(_calc, axis=1, result_type="expand")
        return df

    def handle_dose_groups(self, df: pd.DataFrame) -> pd.DataFrame:
        noel_names = self.kwargs["assessment"].get_noel_names()

        def _func(group_df: pd.DataFrame) -> pd.Series:
            preferred_units = self.get_preferred_units(group_df)
            group_df = group_df[(group_df["dose_group-dose_units_id"] == preferred_units)]
            reported_doses = group_df["dose_group-dose"].mask(
                pd.isna(group_df["endpoint_group-n"])
                & pd.isna(group_df["endpoint_group-response"])
                & pd.isna(group_df["endpoint_group-incidence"])
            )
            doses = (
                group_df["dose_group-dose"]
                if reported_doses.dropna().empty
                else reported_doses.dropna()
            )
            group_df["doses"] = (
                ", ".join(doses.astype(str)) + " " + group_df["dose_group-dose_units_name"]
            )

            if reported_doses.dropna().empty:
                group_df["low_dose"] = None
                group_df["high_dose"] = None
                group_df[noel_names.noel] = None
                group_df[noel_names.loel] = None
                group_df["FEL"] = None
                return group_df
            low_dose_index = reported_doses.iloc[1:].first_valid_index()
            group_df["low_dose"] = (
                None if low_dose_index is None else reported_doses.loc[low_dose_index]
            )
            high_dose_index = reported_doses.iloc[1:].last_valid_index()
            group_df["high_dose"] = (
                None if high_dose_index is None else reported_doses.loc[high_dose_index]
            )
            NOEL_series = group_df["dose_group-dose"][
                group_df["endpoint_group-NOEL"].fillna(False) & pd.notna(reported_doses)
            ]
            group_df[noel_names.noel] = NOEL_series.iloc[0] if NOEL_series.size > 0 else None
            LOEL_series = group_df["dose_group-dose"][
                group_df["endpoint_group-LOEL"].fillna(False) & pd.notna(reported_doses)
            ]
            group_df[noel_names.loel] = LOEL_series.iloc[0] if LOEL_series.size > 0 else None
            FEL_series = group_df["dose_group-dose"][
                group_df["endpoint_group-FEL"].fillna(False) & pd.notna(reported_doses)
            ]
            group_df["FEL"] = FEL_series.iloc[0] if FEL_series.size > 0 else None
            return group_df

        return (
            df.groupby("endpoint-id", group_keys=False, sort=False)
            .apply(_func)
            .reset_index(drop=True)
        )

    def handle_incidence_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        def _func(group_df: pd.DataFrame) -> pd.Series:
            group_df["dichotomous summary"] = "-"
            group_df["percent affected"] = None
            group_df["percent lower ci"] = None
            group_df["percent upper ci"] = None
            data_type = group_df["endpoint-data_type"].iloc[0]

            def __func(row: pd.Series) -> pd.Series:
                # logic used from EndpointGroup.get_incidence_summary()
                n = row["endpoint_group-n"]
                i = row["endpoint_group-incidence"]
                if (
                    data_type
                    in [constants.DataType.DICHOTOMOUS, constants.DataType.DICHOTOMOUS_CANCER]
                    and n is not None
                    and n > 0
                    and i is not None
                ):
                    row["dichotomous summary"] = f"{int(i)}/{int(n)} ({i / n * 100:.1f}%)"
                    row["percent affected"] = i / n * 100
                    row["percent lower ci"] = row["endpoint_group-lower_ci"] * 100
                    row["percent upper ci"] = row["endpoint_group-upper_ci"] * 100
                return row

            return group_df.apply(__func, axis="columns")

        return (
            df.groupby("endpoint-id", group_keys=False, sort=False)
            .apply(_func)
            .reset_index(drop=True)
        )

    def build_df(self) -> pd.DataFrame:
        df = EndpointGroupFlatDataPivotExporter().get_df(
            self.queryset.select_related(
                "animal_group__experiment__study",
                "animal_group__dosing_regime",
            )
            .prefetch_related("groups", "animal_group__dosing_regime__doses")
            .order_by("id", "groups", "animal_group__dosing_regime__doses")
        )
        df = df[
            pd.isna(df["dose_group-id"])
            | (df["endpoint_group-dose_group_id"] == df["dose_group-dose_group_id"])
        ]
        if df.empty:
            return df
        if obj := self.queryset.first():
            endpoint_ids = list(df["endpoint-id"].unique())
            rob_df = get_final_score_df(obj.assessment_id, endpoint_ids, "animal")
            df = df.join(rob_df, on="endpoint-id")

        df["route"] = df["dosing_regime-route_of_exposure_display"].str.lower()
        df["species strain"] = (
            df["animal_group-species_name"] + " " + df["animal_group-strain_name"]
        )

        df["observation time"] = (
            df["endpoint-observation_time"].replace(np.nan, None).astype(str)
            + " "
            + df["endpoint-observation_time_units_display"]
        )

        df = self.handle_stdev(df)
        df = self.handle_ci(df)
        df = self.handle_dose_groups(df)
        df = self.handle_animal_description(df)
        df = self.handle_treatment_period(df)
        df = self.handle_percent_control(df)
        df = self.handle_incidence_summary(df)

        df = df.rename(
            lambda x: x.replace("_udf_content-content-field-", " "),
            axis="columns",
        )

        df = df.rename(
            columns={
                "study-id": "study id",
                "study-short_citation": "study name",
                "study-study_identifier": "study identifier",
                "study-published": "study published",
                "experiment-id": "experiment id",
                "experiment-name": "experiment name",
                "experiment-chemical": "chemical",
                "animal_group-id": "animal group id",
                "animal_group-name": "animal group name",
                "animal_group-lifestage_exposed": "lifestage exposed",
                "animal_group-lifestage_assessed": "lifestage assessed",
                "animal_group-species_name": "species",
                "animal_group-generation": "generation",
                "animal_group-sex_display": "sex",
                "dosing_regime-duration_exposure_text": "duration exposure",
                "dosing_regime-duration_exposure": "duration exposure (days)",
                "endpoint-id": "endpoint id",
                "endpoint-name": "endpoint name",
                "endpoint-system": "system",
                "endpoint-organ": "organ",
                "endpoint-effect": "effect",
                "endpoint-effect_subtype": "effect subtype",
                "endpoint-diagnostic": "diagnostic",
                "endpoint-effects_display": "tags",
                "endpoint-observation_time_text": "observation time text",
                "endpoint-data_type_display": "data type",
                "dose_group-dose_units_name": "dose units",
                "endpoint-response_units": "response units",
                "endpoint-expected_adversity_direction": "expected adversity direction",
                "endpoint-trend_value": "trend test value",
                "endpoint-trend_result_display": "trend test result",
                "endpoint_group-id": "key",
                "endpoint_group-dose_group_id": "dose index",
                "dose_group-dose": "dose",
                "endpoint_group-n": "N",
                "endpoint_group-incidence": "incidence",
                "endpoint_group-response": "response",
                "endpoint_group-stdev": "stdev",
                "endpoint_group-lower_ci": "lower_ci",
                "endpoint_group-upper_ci": "upper_ci",
                "endpoint_group-significant": "pairwise significant",
                "endpoint_group-significance_level": "pairwise significant value",
                "endpoint_group-treatment_effect_display": "treatment related effect",
            }
        )
        df = df.drop(
            columns=[
                "endpoint_udf_content-content",
                "study_udf_content-content",
                "endpoint_udf_content-content",
                "endpoint-observation_time",
                "dose_group-id",
                "dose_group-dose_group_id",
                "experiment-type_display",
                "endpoint_group-FEL",
                "animal_group-sex_symbol",
                "animal_group-strain_name",
                "endpoint_group-LOEL",
                "endpoint-variance_type",
                "dose_group-dose_units_id",
                "endpoint_group-NOEL",
                "endpoint-observation_time_units_display",
                "endpoint_group-variance",
                "endpoint-data_type",
                "dosing_regime-route_of_exposure_display",
            ]
        )

        return df


class EndpointFlatDataPivotExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport(
                "study",
                "animal_group__experiment__study",
                include=("id", "short_citation", "study_identifier", "published"),
            ),
            ModelUDFContentExport(
                "study_udf_content",
                "animal_group__experiment__study__udf_content",
                include=("content",),
            ),
            ExperimentExport(
                "experiment",
                "animal_group__experiment",
                include=("id", "name", "type_display", "chemical"),
            ),
            AnimalGroupExport(
                "animal_group",
                "animal_group",
                include=(
                    "id",
                    "name",
                    "lifestage_exposed",
                    "lifestage_assessed",
                    "species_name",
                    "strain_name",
                    "generation",
                    "sex_display",
                    "sex_symbol",
                ),
            ),
            ModelUDFContentExport(
                "animal_group_udf_content",
                "animal_group__udf_content",
                include=("content",),
            ),
            DosingRegimeExport(
                "dosing_regime",
                "animal_group__dosing_regime",
                include=(
                    "route_of_exposure_display",
                    "duration_exposure_text",
                    "duration_exposure",
                ),
            ),
            EndpointExport(
                "endpoint",
                "",
                include=(
                    "id",
                    "name",
                    "system",
                    "organ",
                    "effect",
                    "effect_subtype",
                    "diagnostic",
                    "effects_display",
                    "observation_time",
                    "observation_time_units_display",
                    "observation_time_text",
                    "variance_type",
                    "data_type",
                    "data_type_display",
                    "trend_value",
                    "trend_result_display",
                    "expected_adversity_direction",
                    "response_units",
                ),
            ),
            ModelUDFContentExport(
                "endpoint_udf_content",
                "udf_content",
                include=("content",),
            ),
            EndpointGroupExport(
                "endpoint_group",
                "groups",
                include=(
                    "id",
                    "dose_group_id",
                    "n",
                    "incidence",
                    "response",
                    "lower_ci",
                    "upper_ci",
                    "significant",
                    "significance_level",
                    "treatment_effect_display",
                    "NOEL",
                    "LOEL",
                    "FEL",
                    "variance",
                ),
            ),
            DoseGroupExport(
                "dose_group",
                "animal_group__dosing_regime__doses",
                include=("id", "dose_units_id", "dose_units_name", "dose_group_id", "dose"),
            ),
        ]


class EndpointFlatDataPivot(EndpointGroupFlatDataPivot):
    def handle_bmd(self, df: pd.DataFrame) -> pd.DataFrame:
        endpoint_ids = df["endpoint-id"].unique()
        sessions = Session.objects.filter(endpoint_id__in=endpoint_ids, active=True)
        bmd_map = defaultdict(list)
        for session in sessions:
            bmd_map[session.endpoint_id].append(session.get_selected_model())
        preferred_units = self.kwargs.get("preferred_units", None)
        df["BMD"] = None
        df["BMDL"] = None

        def _func(row: pd.Series) -> pd.Series:
            bmds = bmd_map[row["endpoint-id"]]
            for bmd in bmds:
                if bmd["dose_units_id"] in preferred_units and bmd["model"] is not None:
                    row["BMD"] = bmd["bmd"]
                    row["BMDL"] = bmd["bmdl"]
                    break
            return row

        return df.apply(_func, axis="columns")

    def handle_flat_doses(self, df: pd.DataFrame) -> pd.DataFrame:
        def _func(group_df: pd.DataFrame) -> pd.Series:
            unique_df = group_df.drop_duplicates(subset="endpoint_group-id").reset_index(drop=True)
            reported_doses = unique_df["dose_group-dose"].mask(
                pd.isna(unique_df["endpoint_group-n"])
                & pd.isna(unique_df["endpoint_group-response"])
                & pd.isna(unique_df["endpoint_group-incidence"])
            )
            num_doses = reported_doses.size

            group_df[[f"Dose {i}" for i in range(1, num_doses + 1)]] = reported_doses.reset_index(
                drop=True
            )

            data_type = unique_df["endpoint-data_type"].iloc[0]
            control_group = unique_df.iloc[0]
            if pd.isna(unique_df["endpoint_group-id"]).all():
                pass
            elif data_type in {
                constants.DataType.CONTINUOUS,
                constants.DataType.PERCENT_DIFFERENCE,
                constants.DataType.DICHOTOMOUS,
                constants.DataType.DICHOTOMOUS_CANCER,
            }:
                if data_type in {
                    constants.DataType.CONTINUOUS,
                    constants.DataType.PERCENT_DIFFERENCE,
                }:
                    field = "endpoint_group-response"
                elif data_type in {
                    constants.DataType.DICHOTOMOUS,
                    constants.DataType.DICHOTOMOUS_CANCER,
                }:
                    field = "percent affected"
                control_resp = control_group[field]
                insignificant = pd.Series(["No"] * num_doses)
                significant = pd.Series(["Yes - ?"] * num_doses)
                significant_up = pd.Series(["Yes - ↑"] * num_doses)
                significant_down = pd.Series(["Yes - ↓"] * num_doses)

                significance = insignificant.mask(
                    (unique_df["endpoint_group-significant"].fillna(False)),
                    significant_down.mask((unique_df[field] > control_resp), significant_up).mask(
                        (
                            (pd.isna(control_resp))
                            | (pd.isna(unique_df[field]))
                            | (unique_df[field] == control_resp)
                        ),
                        significant,
                    ),
                )
                group_df[[f"Significant {i}" for i in range(1, num_doses + 1)]] = significance
            elif data_type == constants.DataType.NR:
                group_df[[f"Significant {i}" for i in range(1, num_doses + 1)]] = pd.Series(
                    ["?"] * num_doses
                )

            group_df[[f"Treatment Related Effect {i}" for i in range(1, num_doses + 1)]] = (
                unique_df["endpoint_group-treatment_effect_display"].reset_index(drop=True)
            )

            return group_df.drop_duplicates(
                subset=group_df.columns[group_df.columns.str.endswith("-id")].difference(
                    ["endpoint_group-id"]
                )
            )

        return (
            df.groupby("endpoint-id", group_keys=False, sort=False)
            .apply(_func)
            .reset_index(drop=True)
        )

    def build_df(self) -> pd.DataFrame:
        df = EndpointFlatDataPivotExporter().get_df(
            self.queryset.select_related(
                "animal_group__experiment__study",
                "animal_group__dosing_regime",
            )
            .prefetch_related("groups", "animal_group__dosing_regime__doses")
            .order_by("id", "groups", "animal_group__dosing_regime__doses")
        )
        df = df[
            pd.isna(df["endpoint_group-id"])
            | pd.isna(df["dose_group-id"])
            | (df["endpoint_group-dose_group_id"] == df["dose_group-dose_group_id"])
        ]
        if df.empty:
            return df
        if obj := self.queryset.first():
            endpoint_ids = list(df["endpoint-id"].unique())
            rob_df = get_final_score_df(obj.assessment_id, endpoint_ids, "animal")
            df = df.join(rob_df, on="endpoint-id")

        df["route"] = df["dosing_regime-route_of_exposure_display"].str.lower()
        df["species strain"] = (
            df["animal_group-species_name"] + " " + df["animal_group-strain_name"]
        )

        df["observation time"] = (
            df["endpoint-observation_time"].replace(np.nan, None).astype(str)
            + " "
            + df["endpoint-observation_time_units_display"]
        )

        df = self.handle_stdev(df)
        df = self.handle_ci(df)
        df = self.handle_incidence_summary(df)
        df = self.handle_dose_groups(df)
        df = self.handle_flat_doses(df)
        df = self.handle_animal_description(df)
        df = self.handle_treatment_period(df)
        df = self.handle_bmd(df)

        df = df.drop_duplicates(subset="endpoint-id")

        df = df.rename(
            lambda x: x.replace("_udf_content-content-field-", " "),
            axis="columns",
        )

        df = df.rename(
            columns={
                "study-id": "study id",
                "study-short_citation": "study name",
                "study-study_identifier": "study identifier",
                "study-published": "study published",
                "experiment-id": "experiment id",
                "experiment-name": "experiment name",
                "experiment-chemical": "chemical",
                "animal_group-id": "animal group id",
                "animal_group-name": "animal group name",
                "animal_group-lifestage_exposed": "lifestage exposed",
                "animal_group-lifestage_assessed": "lifestage assessed",
                "animal_group-species_name": "species",
                "animal_group-generation": "generation",
                "animal_group-sex_display": "sex",
                "dosing_regime-duration_exposure_text": "duration exposure",
                "dosing_regime-duration_exposure": "duration exposure (days)",
                "endpoint-id": "endpoint id",
                "endpoint-name": "endpoint name",
                "endpoint-system": "system",
                "endpoint-organ": "organ",
                "endpoint-effect": "effect",
                "endpoint-effect_subtype": "effect subtype",
                "endpoint-diagnostic": "diagnostic",
                "endpoint-effects_display": "tags",
                "endpoint-observation_time_text": "observation time text",
                "endpoint-data_type_display": "data type",
                "dose_group-dose_units_name": "dose units",
                "endpoint-response_units": "response units",
                "endpoint-expected_adversity_direction": "expected adversity direction",
                "endpoint-trend_value": "trend test value",
                "endpoint-trend_result_display": "trend test result",
            }
        )
        df = df.drop(
            columns=[
                "endpoint_udf_content-content",
                "animal_group_udf_content-content",
                "study_udf_content-content",
                "endpoint_group-stdev",
                "percent lower ci",
                "percent affected",
                "percent upper ci",
                "dichotomous summary",
                "endpoint-variance_type",
                "dose_group-dose",
                "endpoint-data_type",
                "endpoint_group-NOEL",
                "endpoint_group-incidence",
                "endpoint_group-FEL",
                "endpoint_group-treatment_effect_display",
                "dose_group-dose_units_id",
                "endpoint_group-LOEL",
                "dose_group-dose_group_id",
                "endpoint_group-variance",
                "animal_group-sex_symbol",
                "endpoint_group-upper_ci",
                "endpoint_group-significance_level",
                "endpoint_group-response",
                "endpoint_group-lower_ci",
                "endpoint_group-significant",
                "dose_group-id",
                "experiment-type_display",
                "endpoint_group-dose_group_id",
                "endpoint-observation_time_units_display",
                "endpoint_group-n",
                "dosing_regime-route_of_exposure_display",
                "endpoint_group-id",
                "animal_group-strain_name",
                "endpoint-observation_time",
            ]
        )

        return df


class EndpointSummaryExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport(
                "study",
                "animal_group__experiment__study",
                include=("short_citation", "study_identifier"),
            ),
            ExperimentExport(
                "experiment", "animal_group__experiment", include=("chemical", "type_display")
            ),
            AnimalGroupExport(
                "animal_group",
                "animal_group",
                include=(
                    "name",
                    "species_name",
                    "strain_name",
                    "generation",
                    "sex_display",
                    "sex_symbol",
                ),
            ),
            DosingRegimeExport(
                "dosing_regime",
                "animal_group__dosing_regime",
                include=("route_of_exposure_display", "duration_exposure_text"),
            ),
            EndpointExport(
                "endpoint",
                "",
                include=(
                    "id",
                    "url",
                    "name",
                    "system",
                    "organ",
                    "effect",
                    "observation_time_text",
                    "response_units",
                    "data_type",
                ),
            ),
            EndpointGroupExport(
                "endpoint_group",
                "groups",
                include=(
                    "id",
                    "dose_group_id",
                    "n",
                    "incidence",
                    "response",
                    "variance",
                    "significant",
                ),
            ),
            DoseGroupExport(
                "dose_group",
                "animal_group__dosing_regime__doses",
                include=("dose_units_name", "dose_group_id", "dose"),
            ),
        ]


class EndpointSummary(EndpointGroupFlatDataPivot):
    def _set_responses(self, df: pd.DataFrame):
        df["responses"] = None

        def _func(group_df: pd.DataFrame) -> pd.Series:
            unique_df = group_df.drop_duplicates(subset="endpoint_group-id")
            response_series = (
                unique_df["endpoint_group-response"]
                .map("{:g}".format, na_action="ignore")
                .fillna("")
            )
            incidence_series = (
                unique_df["endpoint_group-incidence"]
                .map("{:g}".format, na_action="ignore")
                .fillna("")
            )
            variance_series = (
                unique_df["endpoint_group-variance"]
                .map("{:g}".format, na_action="ignore")
                .fillna("")
            )
            response_or_incidence = incidence_series.mask(
                response_series.str.len() > 0, response_series
            )
            response_or_incidence_with_variance = response_or_incidence.mask(
                (response_or_incidence.str.len() > 0) & (variance_series.str.len() > 0),
                response_or_incidence + " ± " + variance_series,
            )
            group_df["responses"] = [
                response_or_incidence_with_variance.reset_index(drop=True)
            ] * group_df.shape[0]

            return group_df

        return (
            df.groupby("endpoint-id", group_keys=False, sort=False)
            .apply(_func)
            .reset_index(drop=True)
        )

    def _set_ns(self, df: pd.DataFrame):
        df["ns"] = None

        def _func(group_df: pd.DataFrame) -> pd.Series:
            unique_df = group_df.drop_duplicates(subset="endpoint_group-id")
            group_df["ns"] = [
                unique_df["endpoint_group-n"]
                .map("{:g}".format, na_action="ignore")
                .fillna("")
                .reset_index(drop=True)
            ] * group_df.shape[0]

            return group_df

        return (
            df.groupby("endpoint-id", group_keys=False, sort=False)
            .apply(_func)
            .reset_index(drop=True)
        )

    def _set_response_direction(self, df: pd.DataFrame):
        df["response_direction"] = None

        def _func(group_df: pd.DataFrame) -> pd.Series:
            data_type = group_df["endpoint-data_type"].iloc[0]
            control_group = group_df.iloc[0]
            if pd.notna(control_group["endpoint_group-id"]) and pd.isna(
                control_group["endpoint_group-response"]
            ):
                group_df["response_direction"] = "?"
                return group_df
            significant_groups = group_df[group_df["endpoint_group-significant"].fillna(False)]
            if significant_groups.empty:
                group_df["response_direction"] = "↔"
                return group_df
            significant_group = significant_groups.iloc[0]
            if data_type in [constants.DataType.CONTINUOUS, constants.DataType.PERCENT_DIFFERENCE]:
                if (
                    significant_group["endpoint_group-response"]
                    > control_group["endpoint_group-response"]
                ):
                    group_df["response_direction"] = "↑"
                else:
                    group_df["response_direction"] = "↓"
                return group_df
            else:
                group_df["response_direction"] = "↑"
                return group_df

        return (
            df.groupby("endpoint-id", group_keys=False, sort=False)
            .apply(_func)
            .reset_index(drop=True)
        )

    def _set_doses(self, df: pd.DataFrame):
        df["doses"] = None

        def _func(group_df: pd.DataFrame) -> pd.Series:
            def __func(_group_df: pd.DataFrame) -> pd.Series:
                _group_df["doses"] = [
                    _group_df["dose_group-dose"]
                    .map("{:g}".format, na_action="ignore")
                    .fillna("")
                    .reset_index(drop=True)
                ] * _group_df.shape[0]
                return _group_df

            return (
                group_df.groupby("dose_group-dose_units_name", group_keys=False, sort=False)
                .apply(__func)
                .reset_index(drop=True)
            )

        return (
            df.groupby("endpoint-id", group_keys=False, sort=False)
            .apply(_func)
            .reset_index(drop=True)
        )

    def handle_other(self, df: pd.DataFrame) -> pd.DataFrame:
        def _func(series: pd.Series):
            units = series["dose_group-dose_units_name"]
            doses, responses = series["doses"], series["responses"]
            doses, responses = (
                doses.iloc[: min(doses.size, responses.size)],
                responses.iloc[: min(doses.size, responses.size)],
            )
            valid = responses.str.len() > 0
            return ", ".join(doses[valid] + " " + units + ": " + responses[valid])

        df = self._set_responses(df)
        df = self._set_ns(df)
        df = self._set_response_direction(df)
        df = self._set_doses(df)

        df["Dose units"] = df["dose_group-dose_units_name"]
        df["Doses"] = df["doses"].str.join(", ")
        df["N"] = df["ns"].str.join(", ")
        df["Responses"] = df["responses"].str.join(", ")
        df["Doses and responses"] = df.apply(_func, axis="columns", result_type="reduce")
        df["Response direction"] = df["response_direction"]

        return df

    def handle_treatment_period(self, df: pd.DataFrame):
        txt = df["experiment-type_display"].str.lower()
        txt_index = txt.str.find("(")
        txt_updated = (
            txt.to_frame(name="txt")
            .join(txt_index.to_frame(name="txt_index"))
            .apply(
                lambda x: x["txt"] if x["txt_index"] < 0 else x["txt"][: x["txt_index"]],
                axis="columns",
                result_type="reduce",
            )
        ).astype(str)
        df["dosing_regime-duration_exposure_text"] = (
            txt_updated + " (" + df["dosing_regime-duration_exposure_text"]
        ).where(df["dosing_regime-duration_exposure_text"].str.len() > 0) + ")"
        return df

    def build_df(self) -> pd.DataFrame:
        df = EndpointSummaryExporter().get_df(
            self.queryset.select_related(
                "animal_group__experiment__study",
                "animal_group__dosing_regime",
            )
            .prefetch_related("groups", "animal_group__dosing_regime__doses")
            .order_by("id", "groups", "animal_group__dosing_regime__doses")
        )

        df = df[
            (pd.isna(df["endpoint_group-id"]))
            | (df["endpoint_group-dose_group_id"] == df["dose_group-dose_group_id"])
        ]
        if df.empty:
            return df
        df = self.handle_animal_description(df)
        df = self.handle_treatment_period(df)
        df = self.handle_other(df)

        df = df.drop_duplicates(subset=["endpoint-id", "dose_group-dose_units_name"])
        df = df.sort_values(by=["endpoint-id", "dose_group-dose_units_name"])

        df = df.rename(
            columns={
                "animal description (with N)": "animal description (with n)",
                "animal_group-sex_display": "animal_group-sex",
                "dosing_regime-route_of_exposure_display": "dosing_regime-route_of_exposure",
                "animal_group-species_name": "species-name",
                "animal_group-strain_name": "strain-name",
                "endpoint-observation_time_text": "endpoint-observation_time",
            }
        )

        df = df.drop(
            columns=[
                "doses",
                "experiment-type_display",
                "animal description",
                "endpoint_group-incidence",
                "animal_group-sex_symbol",
                "dose_group-dose_units_name",
                "dose_group-dose_group_id",
                "endpoint-data_type",
                "response_direction",
                "responses",
                "endpoint_group-significant",
                "endpoint_group-n",
                "dose_group-dose",
                "endpoint_group-response",
                "endpoint_group-id",
                "animal_group-generation",
                "endpoint_group-dose_group_id",
                "ns",
                "endpoint_group-variance",
            ]
        )

        return df
