from copy import copy
import math

from django.apps import apps
from django.conf import settings

from django.db.models import Exists, OuterRef

from ..common.helper import FlatFileExporter
from ..materialized.models import FinalRiskOfBiasScore
from ..study.models import Study
from ..common.exports import Exporter, ModelExport
from ..common.helper import FlatFileExporter
from ..common.models import sql_display, sql_format, str_m2m
from ..materialized.models import FinalRiskOfBiasScore
from ..study.exports import StudyExport
from . import constants, models

# TODO make a modelexport for dtxsid
# TODO add groups, and dataframe pivot to provide some missing values?
#      or try to use sql
# TODO add minimum dose, maximum dose, number of doses

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

class DSSToxExport(ModelExport):
    def get_value_map(self):
        return {
            "dtxsid": "dtxsid",
            "dashboard_url": "dashboard_url",
            "img_url": "img_url",
            "content": "content",
            "created":"created",
            "last_updated":"last_updated",
        }

    def get_annotation_map(self, query_prefix):
        img_url_str = f"https://api-ccte.epa.gov/chemical/file/image/search/by-dtxsid/{{}}?x-api-key={settings.CCTE_API_KEY}" if settings.CCTE_API_KEY else "https://comptox.epa.gov/dashboard-api/ccdapp1/chemical-files/image/by-dtxsid/{}"
        return {
            "dashboard_url": sql_format("https://comptox.epa.gov/dashboard/dsstoxdb/results?search={}", query_prefix + "dtxsid"),
            "img_url": sql_format(img_url_str, query_prefix + "dtxsid"),
        }


class IVChemicalExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "name": "name",
            "cas": "cas",
            "purity":"purity",
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
            "metabolic_activation_display": sql_display(query_prefix + "metabolic_activation", constants.MetabolicActivation),

        }

class IVCellTypeExport(ModelExport):
    def get_value_map(self):
        return {
            "id": "id",
            "species": "species",
            "strain": "strain",
            "sex": "sex_display",
            "cell_type":"cell_type",
            "tissue":"tissue",
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
            "data_type":"data_type",
            "variance_type":"variance_type",
            "effects": "effects__name",
            "assay_type": "assay_type",
            "short_description":"short_description",
            "response_units":"response_units",
            "observation_time":"observation_time",
            "observation_time_units":"observation_time_units_display",
            "NOEL":"NOEL",
            "LOEL":"LOEL",
            "monotonicity":"monotonicity_display",
            "overall_pattern":"overall_pattern_display",
            "trend_test":"trend_test_display",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "effects__name": str_m2m(query_prefix + "effects__name"),
            "observation_time_units_display": sql_display(query_prefix + "observation_time_units", constants.ObservationTimeUnits),
            "monotonicity_display": sql_display(query_prefix + "monotonicity", constants.Monotonicity),
            "overall_pattern_display": sql_display(query_prefix + "overall_pattern", constants.OverallPattern),
            "trend_test_display": sql_display(query_prefix + "trend_test", constants.TrendTestResult),
        }

class IVEndpointGroupExport(ModelExport):
    def get_value_map(self):
        return {
            "id":"id",
            "dose_group_id": "dose_group_id",
            "dose": "dose",
            "n": "n",
            "response":"response",
            "variance":"variance",
            "difference_control":"difference_control",
            "difference_control_display":"difference_control_display",
            "significant_control":"significant_control_display",
            "cytotoxicity_observed":"cytotoxicity_observed_display",
            "precipitation_observed":"precipitation_observed_display",
        } # do stdev, percentControlMean, percentControlLow, percentControlHigh

    def get_annotation_map(self, query_prefix):
        Observation = type('Observation', (object,), {'choices': constants.OBSERVATION_CHOICES})
        return {
            "difference_control_display": sql_display(query_prefix + "difference_control", constants.DifferenceControl),
            "significant_control_display": sql_display(query_prefix + "significant_control", constants.Significance),
            "cytotoxicity_observed_display": sql_display(query_prefix + "cytotoxicity_observed", Observation),
            "precipitation_observed_display": sql_display(query_prefix + "precipitation_observed", Observation),
        }

class InvitroExporter(Exporter):

    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport(
                "study",
                "experiment__study",
                include=("id","hero_id","pubmed_id","doi","short_citation","study_identifier","published")
            ),
            IVChemicalExport(
                "iv_chemical", "chemical",
            ),
            DSSToxExport("dsstox","chemical__dtxsid",),
            IVExperimentExport(
                "iv_experiment",
                "experiment",
            ),
            IVCellTypeExport("iv_cell_type", "experiment__cell_type",),
            IVEndpointExport(
                "iv_endpoint",
                "",
                exclude=("data_type","variance_type",)
            ),
            IVEndpointGroupExport(
                "iv_endpoint_group",
                "groups",
                include=("dose","difference_control_display","significant_control","cytotoxicity_observed")
            ),
        ]

import pandas as pd
class DataPivotEndpoint2(FlatFileExporter):
    # TODO add category, bmds benchmark
    # otherwise done

    def collapse_dsstox(self,df:pd.DataFrame):
        # condenses the dsstox info into one column
        dsstox_cols = [col for col in df.columns if col.startswith("dsstox-")]
        dsstox_df = df[dsstox_cols]
        dsstox_df.columns = dsstox_df.columns.str[7:]
        df["chemical DTXSID"] = dsstox_df.to_dict(orient="records")
        return df.drop(columns=dsstox_cols)

    def foobar(self,df):
        def _func(_df: pd.DataFrame)->pd.Series:
            row = _df.iloc[0]
            if pd.isna(row["iv_endpoint_group-dose"]):
                row["number of doses"] = 0
                row["minimum dose"] = None
                row["maximum dose"] = None
                row["iv_endpoint-NOEL"] = None
                row["iv_endpoint-LOEL"] = None
                return row.to_frame().T
            row["number of doses"] = _df.shape[0]
            row["minimum dose"] = _df["iv_endpoint_group-dose"].loc[lambda x: x > 0].min()
            row["maximum dose"] = _df["iv_endpoint_group-dose"].loc[lambda x: x > 0].max()
            for i,_row in enumerate(_df.itertuples(index=False,name=None),start=1):
                row[f"Dose {i}"] = _row[_df.columns.get_loc("iv_endpoint_group-dose")]
                row[f"Change Control {i}"] = _row[_df.columns.get_loc("iv_endpoint_group-difference_control_display")]
                row[f"Significant {i}"] = _row[_df.columns.get_loc("iv_endpoint_group-significant_control")]
                row[f"Cytotoxicity {i}"] = _row[_df.columns.get_loc("iv_endpoint_group-cytotoxicity_observed")]
            row["iv_endpoint-NOEL"] = None if row["iv_endpoint-NOEL"] == -999 else _df.iloc[row["iv_endpoint-NOEL"]]["iv_endpoint_group-dose"]
            row["iv_endpoint-LOEL"] = None if row["iv_endpoint-LOEL"] == -999 else _df.iloc[row["iv_endpoint-LOEL"]]["iv_endpoint_group-dose"]
            return row.to_frame().T
        groups = df.groupby("iv_endpoint-id", group_keys=False)
        return groups.apply(_func).drop(columns=["iv_endpoint_group-dose","iv_endpoint_group-difference_control_display","iv_endpoint_group-significant_control","iv_endpoint_group-cytotoxicity_observed"])



    def build_df(self) -> pd.DataFrame:
        df = InvitroExporter().get_df(self.queryset.order_by("id", "groups"))
        study_ids = list(df["study-id"].unique())
        rob_headers, rob_data = FinalRiskOfBiasScore.get_dp_export(
            self.queryset.first().assessment_id,
            study_ids,
            "invitro",
        )
        rob_df = pd.DataFrame(
            data=[
                [rob_data[(study_id, metric_id)] for metric_id in rob_headers.keys()]
                for study_id in study_ids
            ],
            columns=list(rob_headers.values()),
            index=study_ids,
        )
        df = df.join(rob_df, on="study-id")

        df["key"] = df["iv_endpoint-id"]

        df = self.collapse_dsstox(df)
        df = self.foobar(df)




        df = df.rename(
            columns={
                "study-id":"study id",
                "study-hero_id":"study hero_id",
                "study-pubmed_id":"study pubmed_id",
                "study-doi":"study doi",
                "study-short_citation": "study name",
                "study-study_identifier": "study identifier",
                "study-published": "study published",
            }
        )
        df = df.rename(
            columns={
                "iv_chemical-id":"chemical id",
                "iv_chemical-name":"chemical name",
                "iv_chemical-cas":"chemical CAS",
                "iv_chemical-purity":"chemical purity",
                "iv_experiment-id":"IVExperiment id",
                "iv_experiment-dose_units":"Dose units",
                "iv_experiment-metabolic_activation":"Metabolic activation",
                "iv_experiment-transfection":"Transfection",
                "iv_cell_type-id":"IVCellType id",
                "iv_cell_type-species":"cell species",
                "iv_cell_type-strain":"cell strain",
                "iv_cell_type-sex":"cell sex",
                "iv_cell_type-cell_type":"cell type",
                "iv_cell_type-tissue":"cell tissue",
                "iv_endpoint-id":"IVEndpoint id",
                "iv_endpoint-name":"IVEndpoint name",
                "iv_endpoint-effects":"IVEndpoint description tags",
                "iv_endpoint-assay_type":"assay type",
                "iv_endpoint-short_description":"endpoint description",
                "iv_endpoint-response_units":"endpoint response units",
                "iv_endpoint-observation_time":"observation time",
                "iv_endpoint-observation_time_units":"observation time units",
                "iv_endpoint-NOEL":"NOEL",
                "iv_endpoint-LOEL":"LOEL",
                "iv_endpoint-monotonicity":"monotonicity",
                "iv_endpoint-overall_pattern":"overall pattern",
                "iv_endpoint-trend_test":"trend test result",
            }
        )

        return df

class InvitroGroupExporter(Exporter):
    
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport(
                "study",
                "experiment__study",
                include=("id","short_citation","study_identifier","published")
            ),
            IVChemicalExport(
                "iv_chemical", "chemical",
            ),
            DSSToxExport("dsstox","chemical__dtxsid",),
            IVExperimentExport(
                "iv_experiment",
                "experiment",
            ),
            IVCellTypeExport("iv_cell_type", "experiment__cell_type",),
            IVEndpointExport(
                "iv_endpoint",
                "",
            ),
            IVEndpointGroupExport(
                "iv_endpoint_group",
                "groups",
            ),
        ]

class DataPivotEndpointGroup2(FlatFileExporter):

    def collapse_dsstox(self,df:pd.DataFrame):
        # condenses the dsstox info into one column
        dsstox_cols = [col for col in df.columns if col.startswith("dsstox-")]
        dsstox_df = df[dsstox_cols]
        dsstox_df.columns = dsstox_df.columns.str[7:]
        df["chemical DTXSID"] = dsstox_df.to_dict(orient="records")
        return df.drop(columns=dsstox_cols)

    def add_stdevs(self,df):
        df["stdev"] = df.apply(lambda x:models.IVEndpointGroup.stdev(x["iv_endpoint-variance_type"],x["iv_endpoint_group-variance"],x["iv_endpoint_group-n"]),axis="columns")
        return df.drop(columns=["iv_endpoint-variance_type","iv_endpoint_group-variance"])

    def _add_percent_control(self, df: pd.DataFrame) -> pd.DataFrame:

        def _apply_results(_df1: pd.DataFrame):
            control = _df1.iloc[0]

            _df1["low_dose"] = _df1["iv_endpoint_group-dose"].loc[lambda x: x > 0].min()
            _df1["high_dose"] = _df1["iv_endpoint_group-dose"].loc[lambda x: x > 0].max()

            _df1["iv_endpoint-NOEL"] = None if control["iv_endpoint-NOEL"] == -999 else _df1.iloc[control["iv_endpoint-NOEL"]]["iv_endpoint_group-dose"]
            _df1["iv_endpoint-LOEL"] = None if control["iv_endpoint-LOEL"] == -999 else _df1.iloc[control["iv_endpoint-LOEL"]]["iv_endpoint_group-dose"]

            data_type = control["iv_endpoint-data_type"]
            n_1 = control["iv_endpoint_group-n"]
            mu_1 = control["iv_endpoint_group-response"]
            sd_1 = control["stdev"]

            def _apply_result_groups(test: pd.Series):

                if data_type == constants.DataType.CONTINUOUS:
                    n_2 = test["iv_endpoint_group-n"]
                    mu_2 = test["iv_endpoint_group-response"]
                    sd_2 = test["stdev"]
                    test["percent control mean"], test["percent control low"], test["percent control high"] = percent_control(n_1, mu_1, sd_1, n_2, mu_2, sd_2)
                elif data_type == constants.DataType.DICHOTOMOUS:
                    # TODO this seems to be a dead conditional;
                    # invitro has no 'incidence' variables so
                    # nothing is ever computed here
                    pass
                return test
            

            return _df1.apply(_apply_result_groups,axis="columns")


        results = df.groupby("iv_endpoint-id", group_keys=False)
        computed_df = results.apply(_apply_results)
        return computed_df.drop(columns="iv_endpoint-data_type")

    def build_df(self) -> pd.DataFrame:
        df = InvitroGroupExporter().get_df(self.queryset.filter(Exists(models.IVEndpointGroup.objects.filter(endpoint=OuterRef('pk')))).order_by("id", "groups"))
        study_ids = list(df["study-id"].unique())
        rob_headers, rob_data = FinalRiskOfBiasScore.get_dp_export(
            self.queryset.first().assessment_id,
            study_ids,
            "invitro",
        )
        rob_df = pd.DataFrame(
            data=[
                [rob_data[(study_id, metric_id)] for metric_id in rob_headers.keys()]
                for study_id in study_ids
            ],
            columns=list(rob_headers.values()),
            index=study_ids,
        )
        df = df.join(rob_df, on="study-id")

        df["key"] = df["iv_endpoint_group-id"]


        df = self.add_stdevs(df)
        df = self._add_percent_control(df)
        df = self.collapse_dsstox(df)
        df["iv_endpoint_group-difference_control"] = df["iv_endpoint_group-difference_control"].map(models.IVEndpointGroup.DIFFERENCE_CONTROL_SYMBOLS)

        df = df.rename(
            columns={
                "study-id":"study id",
                "study-short_citation": "study name",
                "study-study_identifier": "study identifier",
                "study-published": "study published",
            }
        )
        df = df.rename(
            columns={
                "iv_chemical-id":"chemical id",
                "iv_chemical-name":"chemical name",
                "iv_chemical-cas":"chemical CAS",
                "iv_chemical-dtxsid":"chemical DTXSID",
                "iv_chemical-purity":"chemical purity",
                "iv_experiment-id":"IVExperiment id",
                "iv_experiment-dose_units":"dose units",
                "iv_experiment-metabolic_activation":"metabolic activation",
                "iv_experiment-transfection":"transfection",
                "iv_cell_type-id":"IVCellType id",
                "iv_cell_type-species":"cell species",
                "iv_cell_type-strain":"cell strain",
                "iv_cell_type-sex":"cell sex",
                "iv_cell_type-cell_type":"cell type",
                "iv_cell_type-tissue":"cell tissue",
                "iv_endpoint-id":"IVEndpoint id",
                "iv_endpoint-name":"IVEndpoint name",
                "iv_endpoint-effects":"IVEndpoint description tags",
                "iv_endpoint-assay_type":"assay type",
                "iv_endpoint-short_description":"endpoint description",
                "iv_endpoint-response_units":"endpoint response units",
                "iv_endpoint-observation_time":"observation time",
                "iv_endpoint-observation_time_units":"observation time units",
                "iv_endpoint-NOEL":"NOEL",
                "iv_endpoint-LOEL":"LOEL",
                "iv_endpoint-monotonicity":"monotonicity",
                "iv_endpoint-overall_pattern":"overall pattern",
                "iv_endpoint-trend_test":"trend test result",

            } # need low_dose, high_dose, group specific (ie key and lower)
        ) # find out if name differences are important in visuals; this is similar to regular dp export

        df = df.rename(
            columns={
                "iv_endpoint_group-dose_group_id":"dose index",
                "iv_endpoint_group-dose":"dose",
                "iv_endpoint_group-n":"N",
                "iv_endpoint_group-response":"response",
                "iv_endpoint_group-difference_control":"change from control",
                "iv_endpoint_group-significant_control":"significant from control",
                "iv_endpoint_group-cytotoxicity_observed":"cytotoxicity observed",
                "iv_endpoint_group-precipitation_observed":"precipitation observed",
            }
        )
        return df






def getDose(ser, tag):
    if ser[tag] != -999:
        return ser["groups"][ser[tag]]["dose"]
    else:
        return None


def getDoseRange(ser):
    # get non-zero dose range
    doses = [eg["dose"] for eg in ser["groups"] if eg["dose"] > 0]
    if doses:
        return min(doses), max(doses)
    else:
        return None, None


class DataPivotEndpoint(FlatFileExporter):
    def _get_header_row(self):
        if self.queryset.first() is None:
            self.rob_headers, self.rob_data = {}, {}
        else:
            study_ids = set(self.queryset.values_list("experiment__study_id", flat=True))
            self.rob_headers, self.rob_data = FinalRiskOfBiasScore.get_dp_export(
                self.queryset.first().assessment_id,
                study_ids,
                "invitro",
            )

        header = [
            "study id",
            "study hero_id",
            "study pubmed_id",
            "study doi",
            "study name",
            "study identifier",
            "study published",
        ]

        header.extend(list(self.rob_headers.values()))

        header.extend(
            [
                "chemical id",
                "chemical name",
                "chemical CAS",
                "chemical DTXSID",
                "chemical purity",
                "IVExperiment id",
                "IVCellType id",
                "cell species",
                "cell strain",
                "cell sex",
                "cell type",
                "cell tissue",
                "Dose units",
                "Metabolic activation",
                "Transfection",
                "key",
                "IVEndpoint id",
                "IVEndpoint name",
                "IVEndpoint description tags",
                "assay type",
                "endpoint description",
                "endpoint response units",
                "observation time",
                "observation time units",
                "NOEL",
                "LOEL",
                "monotonicity",
                "overall pattern",
                "trend test result",
                "minimum dose",
                "maximum dose",
                "number of doses",
            ]
        )

        num_cats = 0
        if self.queryset.count() > 0:
            IVEndpointCategory = apps.get_model("invitro", "IVEndpointCategory")
            num_cats = IVEndpointCategory.get_maximum_depth(self.queryset[0].assessment_id)
        header.extend([f"Category {i}" for i in range(1, num_cats + 1)])

        num_doses = self.queryset.model.max_dose_count(self.queryset)
        rng = range(1, num_doses + 1)
        header.extend([f"Dose {i}" for i in rng])
        header.extend([f"Change Control {i}" for i in rng])
        header.extend([f"Significant {i}" for i in rng])
        header.extend([f"Cytotoxicity {i}" for i in rng])

        num_bms = self.queryset.model.max_benchmark_count(self.queryset)
        rng = range(1, num_bms + 1)
        header.extend([f"Benchmark Type {i}" for i in rng])
        header.extend([f"Benchmark Value {i}" for i in rng])

        self.num_cats = num_cats
        self.num_doses = num_doses
        self.num_bms = num_bms

        return header

    def _get_data_rows(self):
        rows = []

        identifiers_df = Study.identifiers_df(self.queryset, "experiment__study_id")

        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)

            doseRange = getDoseRange(ser)

            cats = ser["category"]["names"] if ser["category"] else []

            doses = [eg["dose"] for eg in ser["groups"]]
            diffs = [eg["difference_control"] for eg in ser["groups"]]
            sigs = [eg["significant_control"] for eg in ser["groups"]]
            cytotoxes = [eg["cytotoxicity_observed"] for eg in ser["groups"]]

            if doses and doses[0] == 0:
                doses.pop(0)
                diffs.pop(0)
                sigs.pop(0)

            number_doses = len(doses)

            bm_types = [bm["benchmark"] for bm in ser["benchmarks"]]
            bm_values = [bm["value"] for bm in ser["benchmarks"]]

            study_id = ser["experiment"]["study"]["id"]
            row = [
                study_id,
                identifiers_df["hero_id"].get(study_id),
                identifiers_df["pubmed_id"].get(study_id),
                identifiers_df["doi"].get(study_id),
                ser["experiment"]["study"]["short_citation"],
                ser["experiment"]["study"]["study_identifier"],
                ser["experiment"]["study"]["published"],
            ]

            study_robs = [
                self.rob_data[(study_id, metric_id)] for metric_id in self.rob_headers.keys()
            ]
            row.extend(study_robs)

            row.extend(
                [
                    ser["chemical"]["id"],
                    ser["chemical"]["name"],
                    ser["chemical"]["cas"],
                    ser["chemical"]["dtxsid"],
                    ser["chemical"]["purity"],
                    ser["experiment"]["id"],
                    ser["experiment"]["cell_type"]["id"],
                    ser["experiment"]["cell_type"]["species"],
                    ser["experiment"]["cell_type"]["strain"],
                    ser["experiment"]["cell_type"]["sex"],
                    ser["experiment"]["cell_type"]["cell_type"],
                    ser["experiment"]["cell_type"]["tissue"],
                    ser["experiment"]["dose_units"]["name"],
                    ser["experiment"]["metabolic_activation"],
                    ser["experiment"]["transfection"],
                    ser["id"],  # repeat for data-pivot key
                    ser["id"],
                    ser["name"],
                    "|".join([d["name"] for d in ser["effects"]]),
                    ser["assay_type"],
                    ser["short_description"],
                    ser["response_units"],
                    ser["observation_time"],
                    ser["observation_time_units"],
                    getDose(ser, "NOEL"),
                    getDose(ser, "LOEL"),
                    ser["monotonicity"],
                    ser["overall_pattern"],
                    ser["trend_test"],
                    doseRange[0],
                    doseRange[1],
                    number_doses,
                ]
            )

            # extend rows to include blank placeholders, and apply
            cats.extend([None] * (self.num_cats - len(cats)))
            doses.extend([None] * (self.num_doses - len(doses)))
            diffs.extend([None] * (self.num_doses - len(diffs)))
            sigs.extend([None] * (self.num_doses - len(sigs)))
            cytotoxes.extend([None] * (self.num_doses - len(cytotoxes)))

            bm_types.extend([None] * (self.num_bms - len(bm_types)))
            bm_values.extend([None] * (self.num_bms - len(bm_values)))

            row.extend(cats)
            row.extend(doses)
            row.extend(diffs)
            row.extend(sigs)
            row.extend(cytotoxes)
            row.extend(bm_types)
            row.extend(bm_values)

            rows.append(row)

        return rows


class DataPivotEndpointGroup(FlatFileExporter):
    def _get_header_row(self):
        if self.queryset.first() is None:
            self.rob_headers, self.rob_data = {}, {}
        else:
            study_ids = set(self.queryset.values_list("experiment__study_id", flat=True))
            self.rob_headers, self.rob_data = FinalRiskOfBiasScore.get_dp_export(
                self.queryset.first().assessment_id,
                study_ids,
                "invitro",
            )

        header = [
            "study id",
            "study name",
            "study identifier",
            "study published",
        ]

        header.extend(list(self.rob_headers.values()))

        header.extend(
            [
                "chemical id",
                "chemical name",
                "chemical CAS",
                "chemical DTXSID",
                "chemical purity",
                "IVExperiment id",
                "IVCellType id",
                "cell species",
                "cell strain",
                "cell sex",
                "cell type",
                "cell tissue",
                "dose units",
                "metabolic activation",
                "transfection",
                "IVEndpoint id",
                "IVEndpoint name",
                "IVEndpoint description tags",
                "assay type",
                "endpoint description",
                "endpoint response units",
                "observation time",
                "observation time units",
                "low_dose",
                "NOEL",
                "LOEL",
                "high_dose",
                "monotonicity",
                "overall pattern",
                "trend test result",
                "key",
                "dose index",
                "dose",
                "N",
                "response",
                "stdev",
                "percent control mean",
                "percent control low",
                "percent control high",
                "change from control",
                "significant from control",
                "cytotoxicity observed",
                "precipitation observed",
            ]
        )
        return header

    def _get_data_rows(self):
        rows = []

        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)

            doseRange = getDoseRange(ser)

            row = [
                ser["experiment"]["study"]["id"],
                ser["experiment"]["study"]["short_citation"],
                ser["experiment"]["study"]["study_identifier"],
                ser["experiment"]["study"]["published"],
            ]

            study_id = ser["experiment"]["study"]["id"]
            study_robs = [
                self.rob_data[(study_id, metric_id)] for metric_id in self.rob_headers.keys()
            ]
            row.extend(study_robs)

            row.extend(
                [
                    ser["chemical"]["id"],
                    ser["chemical"]["name"],
                    ser["chemical"]["cas"],
                    ser["chemical"]["dtxsid"],
                    ser["chemical"]["purity"],
                    ser["experiment"]["id"],
                    ser["experiment"]["cell_type"]["id"],
                    ser["experiment"]["cell_type"]["species"],
                    ser["experiment"]["cell_type"]["strain"],
                    ser["experiment"]["cell_type"]["sex"],
                    ser["experiment"]["cell_type"]["cell_type"],
                    ser["experiment"]["cell_type"]["tissue"],
                    ser["experiment"]["dose_units"]["name"],
                    ser["experiment"]["metabolic_activation"],
                    ser["experiment"]["transfection"],
                    ser["id"],
                    ser["name"],
                    "|".join([d["name"] for d in ser["effects"]]),
                    ser["assay_type"],
                    ser["short_description"],
                    ser["response_units"],
                    ser["observation_time"],
                    ser["observation_time_units"],
                    doseRange[0],
                    getDose(ser, "NOEL"),
                    getDose(ser, "LOEL"),
                    doseRange[1],
                    ser["monotonicity"],
                    ser["overall_pattern"],
                    ser["trend_test"],
                ]
            )

            # endpoint-group information
            for i, eg in enumerate(ser["groups"]):
                row_copy = copy(row)
                row_copy.extend(
                    [
                        eg["id"],
                        eg["dose_group_id"],
                        eg["dose"],
                        eg["n"],
                        eg["response"],
                        eg["stdev"],
                        eg["percentControlMean"],
                        eg["percentControlLow"],
                        eg["percentControlHigh"],
                        eg["difference_control_symbol"],
                        eg["significant_control"],
                        eg["cytotoxicity_observed"],
                        eg["precipitation_observed"],
                    ]
                )
                rows.append(row_copy)

        return rows
