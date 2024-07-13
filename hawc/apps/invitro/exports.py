import math

import pandas as pd
from django.db.models import Exists, OuterRef

from ..common.exports import Exporter, ModelExport
from ..common.helper import FlatFileExporter, df_move_column
from ..common.models import sql_display, str_m2m
from ..materialized.exports import get_final_score_df
from ..study.exports import StudyExport
from . import constants, models


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


def assessment_categories(assessment_id: int) -> pd.DataFrame:
    df = models.IVEndpointCategory.as_dataframe(assessment_id, include_root=False).set_index("id")
    df2 = pd.DataFrame(df.nested_name.str.split("|").tolist(), index=df.index).fillna("-")
    df2.columns = [f"Category {i}" for i in range(1, len(df2.columns) + 1)]
    return df2


def handle_categories(df: pd.DataFrame, assessment_id: int) -> pd.DataFrame:
    category_df = assessment_categories(assessment_id)
    df["iv_endpoint-category_id"] = df["iv_endpoint-category_id"].astype("Int64")
    df2 = df.merge(category_df, left_on="iv_endpoint-category_id", right_index=True, how="left")
    if "Category 1" in df2.columns:
        df2 = df_move_column(
            df2, "Category 1", "iv_endpoint-category_id", n_cols=category_df.shape[1]
        )
    return df2.drop(columns=["iv_endpoint-category_id"])


class IVChemicalExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "name": "name",
            "cas": "cas",
            "dtxsid_id": "dtxsid_id",
            "purity": "purity",
        }


class IVExperimentExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "dose_units": "dose_units__name",
            "metabolic_activation": "metabolic_activation_display",
            "transfection": "transfection",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "metabolic_activation_display": sql_display(
                query_prefix + "metabolic_activation", constants.MetabolicActivation
            ),
        }


class IVCellTypeExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "species": "species",
            "strain": "strain",
            "sex": "sex_display",
            "cell_type": "cell_type",
            "tissue": "tissue",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "sex_display": sql_display(query_prefix + "sex", constants.Sex),
        }


class IVEndpointExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "name": "name",
            "data_type": "data_type",
            "category_id": "category_id",
            "variance_type": "variance_type",
            "effects": "effects__name",
            "assay_type": "assay_type",
            "short_description": "short_description",
            "response_units": "response_units",
            "observation_time": "observation_time",
            "observation_time_units": "observation_time_units_display",
            "NOEL": "NOEL",
            "LOEL": "LOEL",
            "monotonicity": "monotonicity_display",
            "overall_pattern": "overall_pattern_display",
            "trend_test": "trend_test_display",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "effects__name": str_m2m(query_prefix + "effects__name"),
            "observation_time_units_display": sql_display(
                query_prefix + "observation_time_units", constants.ObservationTimeUnits
            ),
            "monotonicity_display": sql_display(
                query_prefix + "monotonicity", constants.Monotonicity
            ),
            "overall_pattern_display": sql_display(
                query_prefix + "overall_pattern", constants.OverallPattern
            ),
            "trend_test_display": sql_display(
                query_prefix + "trend_test", constants.TrendTestResult
            ),
        }


class IVEndpointGroupExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "dose_group_id": "dose_group_id",
            "dose": "dose",
            "n": "n",
            "response": "response",
            "variance": "variance",
            "difference_control": "difference_control",
            "difference_control_display": "difference_control_display",
            "significant_control": "significant_control_display",
            "cytotoxicity_observed": "cytotoxicity_observed_display",
            "precipitation_observed": "precipitation_observed_display",
        }

    def get_annotation_map(self, query_prefix):
        Observation = type("Observation", (object,), {"choices": constants.OBSERVATION_CHOICES})
        return {
            "difference_control_display": sql_display(
                query_prefix + "difference_control", constants.DifferenceControl
            ),
            "significant_control_display": sql_display(
                query_prefix + "significant_control", constants.Significance
            ),
            "cytotoxicity_observed_display": sql_display(
                query_prefix + "cytotoxicity_observed", Observation
            ),
            "precipitation_observed_display": sql_display(
                query_prefix + "precipitation_observed", Observation
            ),
        }


class IVBenchmarkExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "benchmark": "benchmark",
            "value": "value",
        }


class InvitroExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport(
                "study",
                "experiment__study",
                include=(
                    "id",
                    "hero_id",
                    "pubmed_id",
                    "doi",
                    "short_citation",
                    "study_identifier",
                    "published",
                ),
            ),
            IVChemicalExport(
                "iv_chemical",
                "chemical",
            ),
            IVExperimentExport(
                "iv_experiment",
                "experiment",
            ),
            IVCellTypeExport(
                "iv_cell_type",
                "experiment__cell_type",
            ),
            IVEndpointExport(
                "iv_endpoint",
                "",
                exclude=(
                    "data_type",
                    "variance_type",
                ),
            ),
            IVEndpointGroupExport(
                "iv_endpoint_group",
                "groups",
                include=(
                    "id",
                    "dose",
                    "difference_control_display",
                    "significant_control",
                    "cytotoxicity_observed",
                ),
            ),
            IVBenchmarkExport(
                "iv_benchmark",
                "benchmarks",
            ),
        ]


class DataPivotEndpoint(FlatFileExporter):
    def handle_dose_groups(self, df: pd.DataFrame) -> pd.DataFrame:
        def _func(group_df: pd.DataFrame) -> pd.Series:
            # handle case with no dose groups
            if group_df["iv_endpoint_group-id"].isna().all():
                group_df["number of doses"] = 0
                group_df["minimum dose"] = None
                group_df["maximum dose"] = None
                group_df["iv_endpoint-NOEL"] = None
                group_df["iv_endpoint-LOEL"] = None
                return group_df
            # only interested in unique, non-control dose groups
            unique_df = group_df.drop_duplicates(subset="iv_endpoint_group-id")
            non_control_df = unique_df.loc[unique_df["iv_endpoint_group-dose"] > 0]
            # add dose related columns
            group_df["number of doses"] = non_control_df.shape[0]
            group_df["minimum dose"] = non_control_df["iv_endpoint_group-dose"].min()
            group_df["maximum dose"] = non_control_df["iv_endpoint_group-dose"].max()
            NOEL_index = unique_df.iloc[0]["iv_endpoint-NOEL"]
            group_df["iv_endpoint-NOEL"] = (
                None if NOEL_index == -999 else unique_df.iloc[NOEL_index]["iv_endpoint_group-dose"]
            )
            LOEL_index = unique_df.iloc[0]["iv_endpoint-LOEL"]
            group_df["iv_endpoint-LOEL"] = (
                None if LOEL_index == -999 else unique_df.iloc[LOEL_index]["iv_endpoint_group-dose"]
            )
            for i, row in enumerate(non_control_df.itertuples(index=False, name=None), start=1):
                group_df[f"Dose {i}"] = row[
                    non_control_df.columns.get_loc("iv_endpoint_group-dose")
                ]
                group_df[f"Change Control {i}"] = row[
                    non_control_df.columns.get_loc("iv_endpoint_group-difference_control_display")
                ]
                group_df[f"Significant {i}"] = row[
                    non_control_df.columns.get_loc("iv_endpoint_group-significant_control")
                ]
                group_df[f"Cytotoxicity {i}"] = row[
                    non_control_df.columns.get_loc("iv_endpoint_group-cytotoxicity_observed")
                ]

            # return a df that is dose group agnostic
            return group_df.drop_duplicates(
                subset=group_df.columns[group_df.columns.str.endswith("-id")].difference(
                    ["iv_endpoint_group-id"]
                )
            )

        return (
            df.groupby("iv_endpoint-id", group_keys=False)
            .apply(_func)
            .drop(
                columns=[
                    "iv_endpoint_group-id",
                    "iv_endpoint_group-dose",
                    "iv_endpoint_group-difference_control_display",
                    "iv_endpoint_group-significant_control",
                    "iv_endpoint_group-cytotoxicity_observed",
                ]
            )
            .reset_index(drop=True)
        )

    def handle_benchmarks(self, df: pd.DataFrame) -> pd.DataFrame:
        def _func(group_df: pd.DataFrame) -> pd.DataFrame:
            # handle case with no benchmarks
            if group_df["iv_benchmark-id"].isna().all():
                # no need to deduplicate, since there should be
                # only one benchmark id: None
                return group_df
            # only interested in unique benchmarks
            unique_df = group_df.drop_duplicates(subset="iv_benchmark-id")
            # add the benchmark columns
            for i, row in enumerate(unique_df.itertuples(index=False, name=None), start=1):
                group_df[f"Benchmark Type {i}"] = row[
                    unique_df.columns.get_loc("iv_benchmark-benchmark")
                ]
                group_df[f"Benchmark Value {i}"] = row[
                    unique_df.columns.get_loc("iv_benchmark-value")
                ]
            # return a df that is benchmark agnostic
            return group_df.drop_duplicates(
                subset=group_df.columns[group_df.columns.str.endswith("-id")].difference(
                    ["iv_benchmark-id"]
                )
            )

        return (
            df.groupby("iv_endpoint-id", group_keys=False)
            .apply(_func)
            .drop(columns=["iv_benchmark-id", "iv_benchmark-benchmark", "iv_benchmark-value"])
            .reset_index(drop=True)
        )

    def build_df(self) -> pd.DataFrame:
        df = InvitroExporter().get_df(
            self.queryset.select_related(
                "experiment__study", "chemical__dtxsid", "experiment__cell_type"
            )
            .prefetch_related("groups", "benchmarks")
            .order_by("id", "groups", "benchmarks")
        )
        if obj := self.queryset.first():
            study_ids = list(df["study-id"].unique())
            rob_df = get_final_score_df(obj.assessment_id, study_ids, "invitro")
            df = df.join(rob_df, on="study-id")

        df["key"] = df["iv_endpoint-id"]

        df = self.handle_dose_groups(df)
        df = self.handle_benchmarks(df)
        df = handle_categories(df, self.kwargs["assessment"].id)

        df = df.rename(
            columns={
                "study-id": "study id",
                "study-hero_id": "study hero_id",
                "study-pubmed_id": "study pubmed_id",
                "study-doi": "study doi",
                "study-short_citation": "study name",
                "study-study_identifier": "study identifier",
                "study-published": "study published",
            }
        )
        df = df.rename(
            columns={
                "iv_chemical-id": "chemical id",
                "iv_chemical-name": "chemical name",
                "iv_chemical-cas": "chemical CAS",
                "iv_chemical-dtxsid_id": "chemical DTXSID",
                "iv_chemical-purity": "chemical purity",
                "iv_experiment-id": "IVExperiment id",
                "iv_experiment-dose_units": "Dose units",
                "iv_experiment-metabolic_activation": "Metabolic activation",
                "iv_experiment-transfection": "Transfection",
                "iv_cell_type-id": "IVCellType id",
                "iv_cell_type-species": "cell species",
                "iv_cell_type-strain": "cell strain",
                "iv_cell_type-sex": "cell sex",
                "iv_cell_type-cell_type": "cell type",
                "iv_cell_type-tissue": "cell tissue",
                "iv_endpoint-id": "IVEndpoint id",
                "iv_endpoint-name": "IVEndpoint name",
                "iv_endpoint-effects": "IVEndpoint description tags",
                "iv_endpoint-assay_type": "assay type",
                "iv_endpoint-short_description": "endpoint description",
                "iv_endpoint-response_units": "endpoint response units",
                "iv_endpoint-observation_time": "observation time",
                "iv_endpoint-observation_time_units": "observation time units",
                "iv_endpoint-NOEL": "NOEL",
                "iv_endpoint-LOEL": "LOEL",
                "iv_endpoint-monotonicity": "monotonicity",
                "iv_endpoint-overall_pattern": "overall pattern",
                "iv_endpoint-trend_test": "trend test result",
            }
        )

        return df


class InvitroGroupExporter(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport(
                "study",
                "experiment__study",
                include=("id", "short_citation", "study_identifier", "published"),
            ),
            IVChemicalExport(
                "iv_chemical",
                "chemical",
            ),
            IVExperimentExport(
                "iv_experiment",
                "experiment",
            ),
            IVCellTypeExport(
                "iv_cell_type",
                "experiment__cell_type",
            ),
            IVEndpointExport(
                "iv_endpoint",
                "",
            ),
            IVEndpointGroupExport(
                "iv_endpoint_group", "groups", exclude=("difference_control_display",)
            ),
        ]


class DataPivotEndpointGroup(FlatFileExporter):
    def handle_stdev(self, df: pd.DataFrame) -> pd.DataFrame:
        df["stdev"] = df.apply(
            lambda x: models.IVEndpointGroup.stdev(
                x["iv_endpoint-variance_type"],
                x["iv_endpoint_group-variance"],
                x["iv_endpoint_group-n"],
            ),
            axis="columns",
        )
        return df.drop(columns=["iv_endpoint-variance_type", "iv_endpoint_group-variance"])

    def handle_dose_groups(self, df: pd.DataFrame) -> pd.DataFrame:
        def _func(group_df: pd.DataFrame) -> pd.DataFrame:
            control = group_df.iloc[0]

            group_df["low_dose"] = group_df["iv_endpoint_group-dose"].loc[lambda x: x > 0].min()
            group_df["high_dose"] = group_df["iv_endpoint_group-dose"].loc[lambda x: x > 0].max()

            group_df["iv_endpoint-NOEL"] = (
                None
                if control["iv_endpoint-NOEL"] == -999
                else group_df.iloc[control["iv_endpoint-NOEL"]]["iv_endpoint_group-dose"]
            )
            group_df["iv_endpoint-LOEL"] = (
                None
                if control["iv_endpoint-LOEL"] == -999
                else group_df.iloc[control["iv_endpoint-LOEL"]]["iv_endpoint_group-dose"]
            )

            data_type = control["iv_endpoint-data_type"]
            n_1 = control["iv_endpoint_group-n"]
            mu_1 = control["iv_endpoint_group-response"]
            sd_1 = control["stdev"]

            def __func(row: pd.Series) -> pd.Series:
                # logic used from IVEndpointGroup.percentControl()
                if data_type == constants.DataType.CONTINUOUS:
                    n_2 = row["iv_endpoint_group-n"]
                    mu_2 = row["iv_endpoint_group-response"]
                    sd_2 = row["stdev"]
                    (
                        row["percent control mean"],
                        row["percent control low"],
                        row["percent control high"],
                    ) = percent_control(n_1, mu_1, sd_1, n_2, mu_2, sd_2)
                elif data_type == constants.DataType.DICHOTOMOUS:
                    # TODO this seems to be a dead conditional;
                    # invitro has no 'incidence' variables so
                    # nothing is ever computed here
                    pass
                return row

            return group_df.apply(__func, axis="columns")

        return (
            df.groupby("iv_endpoint-id", group_keys=False)
            .apply(_func)
            .drop(columns="iv_endpoint-data_type")
            .reset_index(drop=True)
        )

    def build_df(self) -> pd.DataFrame:
        df = InvitroGroupExporter().get_df(
            self.queryset.select_related(
                "experiment__study", "chemical__dtxsid", "experiment__cell_type"
            )
            .prefetch_related("groups")
            .filter(Exists(models.IVEndpointGroup.objects.filter(endpoint=OuterRef("pk"))))
            .order_by("id", "groups")
        )
        if obj := self.queryset.first():
            study_ids = list(df["study-id"].unique())
            rob_df = get_final_score_df(obj.assessment_id, study_ids, "invitro")
            df = df.join(rob_df, on="study-id")

        df["key"] = df["iv_endpoint_group-id"]
        df = df.drop(columns=["iv_endpoint_group-id"])

        df = self.handle_stdev(df)
        df = self.handle_dose_groups(df)
        df = handle_categories(df, self.kwargs["assessment"].id)

        df["iv_endpoint_group-difference_control"] = df["iv_endpoint_group-difference_control"].map(
            models.IVEndpointGroup.DIFFERENCE_CONTROL_SYMBOLS
        )

        df = df.rename(
            columns={
                "study-id": "study id",
                "study-short_citation": "study name",
                "study-study_identifier": "study identifier",
                "study-published": "study published",
            }
        )
        df = df.rename(
            columns={
                "iv_chemical-id": "chemical id",
                "iv_chemical-name": "chemical name",
                "iv_chemical-cas": "chemical CAS",
                "iv_chemical-dtxsid_id": "chemical DTXSID",
                "iv_chemical-purity": "chemical purity",
                "iv_experiment-id": "IVExperiment id",
                "iv_experiment-dose_units": "dose units",
                "iv_experiment-metabolic_activation": "metabolic activation",
                "iv_experiment-transfection": "transfection",
                "iv_cell_type-id": "IVCellType id",
                "iv_cell_type-species": "cell species",
                "iv_cell_type-strain": "cell strain",
                "iv_cell_type-sex": "cell sex",
                "iv_cell_type-cell_type": "cell type",
                "iv_cell_type-tissue": "cell tissue",
                "iv_endpoint-id": "IVEndpoint id",
                "iv_endpoint-name": "IVEndpoint name",
                "iv_endpoint-effects": "IVEndpoint description tags",
                "iv_endpoint-assay_type": "assay type",
                "iv_endpoint-short_description": "endpoint description",
                "iv_endpoint-response_units": "endpoint response units",
                "iv_endpoint-observation_time": "observation time",
                "iv_endpoint-observation_time_units": "observation time units",
                "iv_endpoint-NOEL": "NOEL",
                "iv_endpoint-LOEL": "LOEL",
                "iv_endpoint-monotonicity": "monotonicity",
                "iv_endpoint-overall_pattern": "overall pattern",
                "iv_endpoint-trend_test": "trend test result",
            }
        )
        df = df.rename(
            columns={
                "iv_endpoint_group-dose_group_id": "dose index",
                "iv_endpoint_group-dose": "dose",
                "iv_endpoint_group-n": "N",
                "iv_endpoint_group-response": "response",
                "iv_endpoint_group-difference_control": "change from control",
                "iv_endpoint_group-significant_control": "significant from control",
                "iv_endpoint_group-cytotoxicity_observed": "cytotoxicity observed",
                "iv_endpoint_group-precipitation_observed": "precipitation observed",
            }
        )

        return df
