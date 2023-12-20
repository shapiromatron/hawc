import math

import pandas as pd
import numpy as np
from scipy import stats
from django.db.models import Exists, OuterRef, F
from django.db.models.lookups import Exact



from ..common.exports import Exporter, ModelExport
from ..common.helper import FlatFileExporter
from ..common.helper import cleanHTML
from ..common.models import sql_display, str_m2m, sql_format
from ..materialized.models import FinalRiskOfBiasScore
from ..study.exports import StudyExport
from . import constants, models


def cont_ci(stdev,n,response):
    """
    Two-tailed t-test, assuming 95% confidence interval.
    """
    se = stdev / math.sqrt(n)
    change = stats.t.ppf(0.975, max(n - 1, 1)) * se
    lower_ci = response - change
    upper_ci = response + change
    return lower_ci, upper_ci

def dich_ci(incidence,n):
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
    lower_ci = ((tmp1 - 1) - z * np.sqrt(z2 - (2 + 1 / n) + 4 * p * (n * q + 1))) / (
        2 * (n + z2)
    )
    upper_ci = ((tmp1 + 1) + z * np.sqrt(z2 + (2 + 1 / n) + 4 * p * (n * q - 1))) / (
        2 * (n + z2)
    )
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


class ExperimentExport(ModelExport):
    # experiment
    def get_value_map(self):
        return {
            "id":"id",
            "url":"url",
            "name":"name",
            "type":"type_display",
            "has_multiple_generations":"has_multiple_generations",
            "chemical":"chemical",
            "cas":"cas",
            "dtxsid":"dtxsid",
            "chemical_source":"chemical_source",
            "purity_available":"purity_available",
            "purity_qualifier":"purity_qualifier",
            "purity":"purity",
            "vehicle":"vehicle",
            "guideline_compliance":"guideline_compliance",
            "description":"description",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "url": sql_format("/ani/experiment/{}/", query_prefix + "id"),  # hardcoded URL
            "type_display": sql_display(
                query_prefix + "type", constants.ExperimentType
            ),
        }

    def prepare_df(self, df):
        # clean html text
        description = self.get_column_name("description")
        if description in df.columns:
            df.loc[:, description] = df[description].apply(cleanHTML)
        return df

class AnimalGroupExport(ModelExport):
    # animal_group
    def get_value_map(self):
        return {
            "id":"id",
            "url":"url",
            "name":"name",
            "sex":"sex_display",
            "sex_symbol":"sex_symbol",
            "animal_source":"animal_source",
            "lifestage_exposed":"lifestage_exposed",
            "lifestage_assessed":"lifestage_assessed",
            "siblings":"siblings",
            "parents":"parents_display",
            "generation":"generation",
            "comments":"comments",
            "diet":"diet",
            "species":"species__name",
            "strain":"strain__name",
        }
    def get_annotation_map(self, query_prefix):
        SexSymbol = type("SexSymbol", (object,), {"choices": models.AnimalGroup.SEX_SYMBOLS.items()})
        return {
            "url": sql_format("/ani/animal-group/{}/", query_prefix + "id"),  # hardcoded URL
            "sex_display": sql_display(
                query_prefix + "sex", constants.Sex
            ),
            "sex_symbol": sql_display(
                query_prefix + "sex", SexSymbol
            ),
            "parents_display": str_m2m(query_prefix + "parents__name"),
        }

    def prepare_df(self, df):
        # clean html text
        comments = self.get_column_name("comments")
        if comments in df.columns:
            df.loc[:, comments] = df[comments].apply(cleanHTML)
        return df


class DosingRegimeExport(ModelExport):
    # dosing_regime
    def get_value_map(self):
        return {
            "id":"id",
            "dosed_animals":"dosed_animals",
            "route_of_exposure":"route_of_exposure_display",
            "duration_exposure":"duration_exposure",
            "duration_exposure_text":"duration_exposure_text",
            "duration_observation":"duration_observation",
            "num_dose_groups":"num_dose_groups",
            "positive_control":"positive_control_display",
            "negative_control":"negative_control_display",
            "description":"description",
        }

    def get_annotation_map(self, query_prefix):
        PositiveControl = type("PositiveControl", (object,), {"choices": constants.POSITIVE_CONTROL_CHOICES})
        return {
            "route_of_exposure_display": sql_display(
                query_prefix + "route_of_exposure", constants.RouteExposure
            ),
            "positive_control_display": sql_display(
                query_prefix + "positive_control", PositiveControl
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
    # endpoint
    def get_value_map(self):
        return {
            "id":"id",
            "url":"url",
            "name":"name",
            "effects":"effects_display",
            "system":"system",
            "organ":"organ",
            "effect":"effect",
            "effect_subtype":"effect_subtype",
            "name_term_id":"name_term_id",
            "system_term_id":"system_term_id",
            "organ_term_id":"organ_term_id",
            "effect_term_id":"effect_term_id",
            "effect_subtype_term_id":"effect_subtype_term_id",
            "litter_effects":"litter_effects",
            "litter_effect_notes":"litter_effect_notes",
            "observation_time":"observation_time",
            "observation_time_units":"observation_time_units_display",
            "observation_time_text":"observation_time_text",
            "data_location":"data_location",
            "response_units":"response_units",
            "data_type":"data_type",
            "variance_type":"variance_type",
            "variance_type_name":"variance_type_name",
            "confidence_interval":"confidence_interval",
            "data_reported":"data_reported",
            "data_extracted":"data_extracted",
            "values_estimated":"values_estimated",
            "expected_adversity_direction":"expected_adversity_direction_display",
            "monotonicity":"monotonicity_display",
            "statistical_test":"statistical_test",
            "trend_value":"trend_value",
            "trend_result":"trend_result_display",
            "diagnostic":"diagnostic",
            "power_notes":"power_notes",
            "results_notes":"results_notes",
            "endpoint_notes":"endpoint_notes",
            "additional_fields":"additional_fields",
        }

    def get_annotation_map(self, query_prefix):
        VarianceName = type("VarianceName", (object,), {"choices": models.Endpoint.VARIANCE_NAME.items()})
        return {
            "url": sql_format("/ani/endpoint/{}/", query_prefix + "id"),  # hardcoded URL
            "effects_display": str_m2m(query_prefix + "effects__name"),
            "observation_time_units_display": sql_display(
                query_prefix + "observation_time_units", constants.ObservationTimeUnits
            ),
            "variance_type_name": sql_display(
                query_prefix + "variance_type", VarianceName
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
    # endpoint_group
    def get_value_map(self):
        return {
            "id":"id",
            "dose_group_id":"dose_group_id",
            "n":"n",
            "incidence":"incidence",
            "response":"response",
            "variance":"variance",
            "lower_ci":"lower_ci",
            "upper_ci":"upper_ci",
            "significant":"significant",
            "significance_level":"significance_level",
            "treatment_effect":"treatment_effect",
            "NOEL":"NOEL",
            "LOEL":"LOEL",
            "FEL":"FEL",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "NOEL": Exact(F(query_prefix+"dose_group_id"),F(query_prefix+"endpoint__NOEL")),
            "LOEL": Exact(F(query_prefix+"dose_group_id"),F(query_prefix+"endpoint__LOEL")),
            "FEL": Exact(F(query_prefix+"dose_group_id"),F(query_prefix+"endpoint__FEL")),
        }

class DoseGroupExport(ModelExport):
    # dose_group
    def get_value_map(self):
        return {
            "id":"id",
            "dose_units_id":"dose_units__id",
            "dose_units_name":"dose_units__name",
            "dose_group_id":"dose_group_id",
            "dose":"dose",
        }


class AnimalExporter(Exporter):
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
            AnimalGroupExport(
                "animal_group",
                "animal_group",
            ),
            DosingRegimeExport(
                "dosing_regime",
                "animal_group__dosing_regime",
            ),
            EndpointExport(
                "endpoint",
                "",
            ),
            EndpointGroupExport(
                "endpoint_group",
                "groups",
            ),
            DoseGroupExport(
                "dose_group",
                "animal_group__dosing_regime__doses",
            )
        ]

### FIRST
class EndpointGroupFlatComplete2(FlatFileExporter):



    def handle_doses(self,df: pd.DataFrame) -> pd.DataFrame:
        # this is really slow; maybe its the filtering to find matching dose group ids?
        # solutions: ?, put the burden on SQL w/ Prefetch and Subquery (messy)
        # long term solutions: group and dose group should be related
        def _func(group_df: pd.DataFrame) -> pd.DataFrame:
            # handle case with no dose data
            if group_df["dose_group-id"].isna().all():
                return group_df

            # add dose data
            group_df["doses-"+group_df["dose_group-dose_units_name"]] = group_df["dose_group-dose"].tolist()

            # return a df that is dose agnostic
            return group_df.drop_duplicates(
                subset=group_df.columns[group_df.columns.str.endswith("-id")].difference(
                    ["dose_group-id"]
                )
            )

        return (
            df.groupby("endpoint_group-id", group_keys=False)
            .apply(_func)
            .drop(columns=["dose_group-id", "dose_group-dose_units_name", "dose_group-dose_group_id","dose_group-dose"])
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
            elif data_type == constants.DataType.CONTINUOUS and response is not None and stdev is not None:
                (
                    row["endpoint_group-lower_ci"],
                    row["endpoint_group-upper_ci"],
                ) = cont_ci(stdev,n,response)
            elif data_type in [constants.DataType.DICHOTOMOUS,constants.DataType.DICHOTOMOUS_CANCER] and incidence is not None:
                (
                    row["endpoint_group-lower_ci"],
                    row["endpoint_group-upper_ci"],
                ) = dich_ci(incidence,n)
            return row

        return df.apply(_func, axis="columns").drop(columns=["endpoint_group-stdev"])

    def build_df(self) -> pd.DataFrame:
        df = AnimalExporter().get_df(
            self.queryset.select_related(
                "animal_group__experiment__study", "animal_group__dosing_regime",
            )
            .prefetch_related("groups",)
            .order_by("id", "groups",)
        )
        df = df[pd.isna(df["dose_group-id"])|(df["endpoint_group-dose_group_id"]==df["dose_group-dose_group_id"])]
        if obj := self.queryset.first():
            doses = DoseUnits.objects.get_animal_units_names(obj.assessment_id)

            df = df.assign(**{f"doses-{d}":None for d in doses})
            df = self.handle_doses(df) # really slow
        df = self.handle_stdev(df)
        df = self.handle_ci(df)

        df = df.rename(
            columns={
                "endpoint-variance_type_name":"endpoint-variance_type",
                "animal_group-species": "species-name",
                "animal_group-strain": "strain-name",
            }
        )



        return df


class AnimalExporter2(Exporter):
    def build_modules(self) -> list[ModelExport]:
        return [
            StudyExport(
                "study",
                "animal_group__experiment__study",
                include=("id","short_citation","study_identifier","published")
            ),
            ExperimentExport(
                "experiment",
                "animal_group__experiment",
                include=("id","name","type","chemical")
            ),
            AnimalGroupExport(
                "animal_group",
                "animal_group",
                include=("id","name","lifestage_exposed","lifestage_assessed","species","strain","generation","sex","sex_symbol")
            ),
            DosingRegimeExport(
                "dosing_regime",
                "animal_group__dosing_regime",
                include=("route_of_exposure","duration_exposure_text","duration_exposure")
            ),
            EndpointExport(
                "endpoint",
                "",
                include=("id","name","system","organ","effect","effect_subtype","diagnostic","effects","observation_time","observation_time_units","observation_time_text")
            ),
            EndpointGroupExport(
                "endpoint_group",
                "groups",
                include=("id","dose_group_id","n","incidence","response","lower_ci","upper_ci","significant","significance_level","treatment_effect","NOEL","LOEL","FEL")
            ),
            DoseGroupExport(
                "dose_group",
                "animal_group__dosing_regime__doses",
                include=("id","dose_units_id","dose_units_name","dose_group_id","dose")
            )
        ]

### SECOND
class EndpointGroupFlatDataPivot2(FlatFileExporter):

    def get_preferred_units(self,df:pd.DataFrame):
        preferred_units = self.kwargs.get("preferred_units", None)
        available_units = df["dose_group-dose_units_id"].dropna().unique()
        if available_units.size == 0:
            return None
        if preferred_units:
            for units in preferred_units:
                if units in available_units:
                    return units
        return available_units[0]


    def handle_animal_description(self,df:pd.DataFrame):
        def _func(group_df: pd.DataFrame) -> pd.Series:
            gen = group_df["animal_group-generation"].iloc[0]
            if len(gen) > 0:
                gen += " "
            ns_txt = ""
            ns = group_df["endpoint_group-n"].dropna().tolist()
            if len(ns) > 0:
                ns_txt = ", N=" + models.EndpointGroup.getNRangeText(ns)

            sex_symbol = group_df["animal_group-sex_symbol"].iloc[0]
            if sex_symbol == "NR":
                sex_symbol = "sex=NR"
            species = group_df["animal_group-species"].iloc[0]
            strain = group_df["animal_group-strain"].iloc[0]
            group_df["animal description"] = f"{gen}{species}, {strain} ({sex_symbol})"
            group_df["animal description (with N)"] = f"{gen}{species}, {strain} ({sex_symbol}{ns_txt})"

            return group_df


        return (
            df.groupby("endpoint-id", group_keys=False)
            .apply(_func)
            .drop(
                columns=[
                ]
            )
            .reset_index(drop=True)
        )



    def handle_treatment_period(self,df:pd.DataFrame):
        txt = df["experiment-type"].str.lower()
        txt_index =txt.str.find("(")
        txt_updated = txt.to_frame(name="txt").join(txt_index.to_frame(name="txt_index")).apply(lambda x: x["txt"] if x["txt_index"] < 0 else x["txt"][:x["txt_index"]],axis="columns")
        df["treatment period"] = (txt_updated + df["dosing_regime-duration_exposure_text"]).where(df["dosing_regime-duration_exposure_text"])
        return df

    def handle_dose_groups(self, df: pd.DataFrame) -> pd.DataFrame:
        noel_names = self.kwargs["assessment"].get_noel_names()
        def _func(group_df: pd.DataFrame) -> pd.Series:
            if group_df.shape[0] <= 1:
                group_df["low_dose"] = None
                group_df["high_dose"] = None
                group_df[noel_names.noel] = None
                group_df[noel_names.loel] = None
                group_df["FEL"] = None
                return group_df
            group_df["low_dose"] = group_df["dose_group-dose"].iloc[1]
            group_df["high_dose"] = group_df["dose_group-dose"].iloc[-1]
            NOEL_series = group_df["dose_group-dose"][group_df["endpoint_group-NOEL"]]
            group_df[noel_names.noel] = NOEL_series.iloc[0] if NOEL_series.size > 0 else None
            LOEL_series = group_df["dose_group-dose"][group_df["endpoint_group-LOEL"]]
            group_df[noel_names.loel] = LOEL_series.iloc[0] if LOEL_series.size > 0 else None
            FEL_series = group_df["dose_group-dose"][group_df["endpoint_group-FEL"]]
            group_df["FEL"] = FEL_series.iloc[0] if FEL_series.size > 0 else None
            return group_df


        return (
            df.groupby("endpoint-id", group_keys=False)
            .apply(_func)
            .drop(
                columns=[
                ]
            )
            .reset_index(drop=True)
        )







    def build_df(self) -> pd.DataFrame:
        df = AnimalExporter2().get_df(
            self.queryset.select_related(
                "animal_group__experiment__study", "animal_group__dosing_regime",
            )
            .prefetch_related("groups",)
            .order_by("id", "groups",)
        )
        df = df[pd.isna(df["dose_group-id"])|(df["endpoint_group-dose_group_id"]==df["dose_group-dose_group_id"])]

        preferred_units = self.get_preferred_units(df)
        df = df[df["dose_group-dose_units_id"]==preferred_units]


        if obj := self.queryset.first():
            endpoint_ids = list(df["endpoint-id"].unique())
            rob_headers, rob_data = FinalRiskOfBiasScore.get_dp_export(
                obj.assessment_id,
                endpoint_ids,
                "animal",
            )
            rob_df = pd.DataFrame(
                data=[
                    [rob_data[(endpoint_id, metric_id)] for metric_id in rob_headers.keys()]
                    for endpoint_id in endpoint_ids
                ],
                columns=list(rob_headers.values()),
                index=endpoint_ids,
            )
            df = df.join(rob_df, on="study-id")

        df["species strain"] = df["animal_group-species"] + " " +df["animal_group-strain"]

        df["observation time"] = df["endpoint-observation_time"].astype(str) + " " + df["endpoint-observation_time_units"]

        df = self.handle_dose_groups(df)
        df = self.handle_animal_description(df)
        df = self.handle_treatment_period(df)

        df = df.rename(
            columns={
                "study-id": "study id",
                "study-short_citation": "study name",
                "study-study_identifier": "study identifier",
                "study-published": "study published",
                "experiment-id":"experiment id",
                "experiment-name":"experiment name",
                "experiment-chemical":"chemical",
                "animal_group-id":"animal group id",
                "animal_group-name":"animal group name",
                "animal_group-lifestage_exposed":"lifestage exposed",
                "animal_group-lifestage_assessed":"lifestage assessed",
                "animal_group-species":"species",
                "animal_group-generation":"generation",
                "animal_group-sex":"sex",
                "dosing_regime-route_of_exposure":"route",
                "dosing_regime-duration_exposure_text":"duration exposure",
                "dosing_regime-duration_exposure":"duration exposure (days)",
                "endpoint-id":"endpoint id",
                "endpoint-name":"endpoint name",
                "endpoint-system":"system",
                "endpoint-organ":"organ",
                "endpoint-effect":"effect",
                "endpoint-effect_subtype":"effect subtype",
                "endpoint-diagnostic":"diagnostic",
                "endpoint-effects":"tags",
                #"observation time",
                "endpoint-observation_time_text":"observation time text",
                #"data type",
                #"doses",
                #"dose units",
                "endpoint-response_units":"response units",
                "endpoint-expected_adversity_direction":"expected adversity direction",
                #"maximum endpoint change",
                "endpoint-trend_value":"trend test value",
                "endpoint-trend_result":"trend test result",
                #"key",
                "endpoint_group-dose_group_id":"dose index",
                #"dose",
                "endpoint_group-n":"N",
                "endpoint_group-incidence":"incidence",
                "endpoint_group-response":"response",
                #"stdev",
                "endpoint_group-lower_ci":"lower_ci",
                "endpoint_group-upper_ci":"upper_ci",
                "endpoint_group-significant":"pairwise significant",
                "endpoint_group-significance_level":"pairwise significant value",
                "endpoint_group-treatment_effect":"treatment related effect",
                #"percent control mean",
                #"percent control low",
                #"percent control high",
                #"dichotomous summary",
                #"percent affected",
                #"percent lower ci",
                #"percent upper ci",
            }
        )

        return df

### THIRD
class EndpointFlatDataPivot2(FlatFileExporter):

    def build_df(self) -> pd.DataFrame:
        df = AnimalExporter().get_df(
            self.queryset.select_related(
                "animal_group__experiment__study", "animal_group__dosing_regime",
            )
            .prefetch_related("groups",)
            .order_by("id", "groups",)
        )

        return df


### FOURTH
class EndpointSummary2(FlatFileExporter):

    def build_df(self) -> pd.DataFrame:
        df = AnimalExporter().get_df(
            self.queryset.select_related(
                "animal_group__experiment__study", "animal_group__dosing_regime",
            )
            .prefetch_related("groups",)
            .order_by("id", "groups",)
        )

        return df


















from copy import copy

from ..assessment.models import DoseUnits
from ..common.helper import FlatFileExporter
from ..materialized.models import FinalRiskOfBiasScore
from ..study.models import Study
from . import constants, models


def get_gen_species_strain_sex(e, withN=False):
    gen = e["animal_group"]["generation"]
    if len(gen) > 0:
        gen += " "

    ns_txt = ""
    if withN:
        ns = [eg["n"] for eg in e["groups"] if eg["n"] is not None]
        if len(ns) > 0:
            ns_txt = ", N=" + models.EndpointGroup.getNRangeText(ns)

    sex_symbol = e["animal_group"]["sex_symbol"]
    if sex_symbol == "NR":
        sex_symbol = "sex=NR"

    return (
        f"{gen}{e['animal_group']['species']}, {e['animal_group']['strain']} ({sex_symbol}{ns_txt})"
    )


def get_treatment_period(exp, dr):
    txt = exp["type"].lower()
    if txt.find("(") >= 0:
        txt = txt[: txt.find("(")]

    if dr["duration_exposure_text"]:
        txt = f"{txt} ({dr['duration_exposure_text']})"

    return txt


def get_significance_and_direction(data_type, groups):
    """
    Get significance and direction; return all possible values as strings.
    """
    significance_list = []

    if len(groups) == 0:
        return significance_list

    if data_type in {
        constants.DataType.CONTINUOUS,
        constants.DataType.PERCENT_DIFFERENCE,
        constants.DataType.DICHOTOMOUS,
        constants.DataType.DICHOTOMOUS_CANCER,
    }:
        if data_type in {
            constants.DataType.CONTINUOUS,
            constants.DataType.PERCENT_DIFFERENCE,
        }:
            field = "response"
        elif data_type in {
            constants.DataType.DICHOTOMOUS,
            constants.DataType.DICHOTOMOUS_CANCER,
        }:
            field = "percent_affected"
        else:
            raise ValueError(f"Unreachable code? data_type={data_type}")
        control_resp = groups[0][field]
        for group in groups:
            if group["significant"]:
                resp = group[field]
                if control_resp is None or resp is None or resp == control_resp:
                    significance_list.append("Yes - ?")
                elif resp > control_resp:
                    significance_list.append("Yes - ↑")
                else:
                    significance_list.append("Yes - ↓")
            else:
                significance_list.append("No")
    elif data_type == constants.DataType.NR:
        for group in groups:
            significance_list.append("?")
    else:
        raise ValueError("Unreachable code - unable to determine significance/direction")

    return significance_list


class EndpointGroupFlatComplete(FlatFileExporter):
    """
    Returns a complete export of all data required to rebuild the the
    animal bioassay study type from scratch.
    """

    def _get_header_row(self):
        self.doses = DoseUnits.objects.get_animal_units_names(self.kwargs.get("assessment"))

        header = []
        header.extend(Study.flat_complete_header_row())
        header.extend(models.Experiment.flat_complete_header_row())
        header.extend(models.AnimalGroup.flat_complete_header_row())
        header.extend(models.DosingRegime.flat_complete_header_row())
        header.extend(models.Endpoint.flat_complete_header_row())
        header.extend([f"doses-{d}" for d in self.doses])
        header.extend(models.EndpointGroup.flat_complete_header_row())
        return header

    def _get_data_rows(self):
        rows = []
        identifiers_df = Study.identifiers_df(self.queryset, "animal_group__experiment__study_id")
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = []
            row.extend(
                Study.flat_complete_data_row(
                    ser["animal_group"]["experiment"]["study"], identifiers_df
                )
            )
            row.extend(models.Experiment.flat_complete_data_row(ser["animal_group"]["experiment"]))
            row.extend(models.AnimalGroup.flat_complete_data_row(ser["animal_group"]))
            ser_dosing_regime = ser["animal_group"]["dosing_regime"]
            row.extend(models.DosingRegime.flat_complete_data_row(ser_dosing_regime))
            row.extend(models.Endpoint.flat_complete_data_row(ser))
            for i, eg in enumerate(ser["groups"]):
                row_copy = copy(row)
                ser_doses = ser_dosing_regime["doses"] if ser_dosing_regime else None
                row_copy.extend(
                    models.DoseGroup.flat_complete_data_row(ser_doses, self.doses, i)
                    if ser_doses
                    else [None for _ in self.doses]
                )
                row_copy.extend(models.EndpointGroup.flat_complete_data_row(eg, ser))
                rows.append(row_copy)

        return rows


class EndpointGroupFlatDataPivot(FlatFileExporter):
    """
    Return a subset of frequently-used data for generation of data-pivot
    visualizations.
    """

    @classmethod
    def _get_doses_list(cls, ser, preferred_units):
        # compact the dose-list to only one set of dose-units; using the
        # preferred units if available, else randomly get first available
        units_id = None

        if preferred_units:
            available_units = set(
                [d["dose_units"]["id"] for d in ser["animal_group"]["dosing_regime"]["doses"]]
            )
            for units in preferred_units:
                if units in available_units:
                    units_id = units
                    break

        if units_id is None:
            units_id = ser["animal_group"]["dosing_regime"]["doses"][0]["dose_units"]["id"]

        return [
            d
            for d in ser["animal_group"]["dosing_regime"]["doses"]
            if units_id == d["dose_units"]["id"]
        ]

    @classmethod
    def _get_dose_units(cls, doses: list[dict]) -> str:
        return doses[0]["dose_units"]["name"]

    @classmethod
    def _get_doses_str(cls, doses: list[dict]) -> str:
        if len(doses) == 0:
            return ""
        values = ", ".join([str(float(d["dose"])) for d in doses])
        return f"{values} {cls._get_dose_units(doses)}"

    @classmethod
    def _get_dose(cls, doses: list[dict], idx: int) -> float | None:
        for dose in doses:
            if dose["dose_group_id"] == idx:
                return float(dose["dose"])
        return None

    @classmethod
    def _get_species_strain(cls, e):
        return f"{e['animal_group']['species']} {e['animal_group']['strain']}"

    @classmethod
    def _get_observation_time_and_time_units(cls, e):
        return f"{e['observation_time']} {e['observation_time_units']}"

    def _get_header_row(self):
        # move qs.distinct() call here so we can make qs annotations.
        self.queryset = self.queryset.distinct("pk")
        if self.queryset.first() is None:
            self.rob_headers, self.rob_data = {}, {}
        else:
            endpoint_ids = set(self.queryset.values_list("id", flat=True))
            self.rob_headers, self.rob_data = FinalRiskOfBiasScore.get_dp_export(
                self.queryset.first().assessment_id,
                endpoint_ids,
                "animal",
            )

        noel_names = self.kwargs["assessment"].get_noel_names()
        headers = [
            "study id",
            "study name",
            "study identifier",
            "study published",
            "experiment id",
            "experiment name",
            "chemical",
            "animal group id",
            "animal group name",
            "lifestage exposed",
            "lifestage assessed",
            "species",
            "species strain",
            "generation",
            "animal description",
            "animal description (with N)",
            "sex",
            "route",
            "treatment period",
            "duration exposure",
            "duration exposure (days)",
            "endpoint id",
            "endpoint name",
            "system",
            "organ",
            "effect",
            "effect subtype",
            "diagnostic",
            "tags",
            "observation time",
            "observation time text",
            "data type",
            "doses",
            "dose units",
            "response units",
            "expected adversity direction",
            "maximum endpoint change",
            "low_dose",
            "high_dose",
            noel_names.noel,
            noel_names.loel,
            "FEL",
            "trend test value",
            "trend test result",
            "key",
            "dose index",
            "dose",
            "N",
            "incidence",
            "response",
            "stdev",
            "lower_ci",
            "upper_ci",
            "pairwise significant",
            "pairwise significant value",
            "treatment related effect",
            "percent control mean",
            "percent control low",
            "percent control high",
            "dichotomous summary",
            "percent affected",
            "percent lower ci",
            "percent upper ci",
        ]
        headers.extend(list(self.rob_headers.values()))

        return headers

    def _get_data_rows(self):
        preferred_units = self.kwargs.get("preferred_units", None)

        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            doses = self._get_doses_list(ser, preferred_units)
            endpoint_robs = [
                self.rob_data[(ser["id"], metric_id)] for metric_id in self.rob_headers.keys()
            ]

            # build endpoint-group independent data
            row = [
                ser["animal_group"]["experiment"]["study"]["id"],
                ser["animal_group"]["experiment"]["study"]["short_citation"],
                ser["animal_group"]["experiment"]["study"]["study_identifier"],
                ser["animal_group"]["experiment"]["study"]["published"],
                ser["animal_group"]["experiment"]["id"],
                ser["animal_group"]["experiment"]["name"],
                ser["animal_group"]["experiment"]["chemical"],
                ser["animal_group"]["id"],
                ser["animal_group"]["name"],
                ser["animal_group"]["lifestage_exposed"],
                ser["animal_group"]["lifestage_assessed"],
                ser["animal_group"]["species"],
                self._get_species_strain(ser),
                ser["animal_group"]["generation"],
                get_gen_species_strain_sex(ser, withN=False),
                get_gen_species_strain_sex(ser, withN=True),
                ser["animal_group"]["sex"],
                ser["animal_group"]["dosing_regime"]["route_of_exposure"].lower(),
                get_treatment_period(
                    ser["animal_group"]["experiment"],
                    ser["animal_group"]["dosing_regime"],
                ),
                ser["animal_group"]["dosing_regime"]["duration_exposure_text"],
                ser["animal_group"]["dosing_regime"]["duration_exposure"],
                ser["id"],
                ser["name"],
                ser["system"],
                ser["organ"],
                ser["effect"],
                ser["effect_subtype"],
                ser["diagnostic"],
                self.get_flattened_tags(ser, "effects"),
                self._get_observation_time_and_time_units(ser),
                ser["observation_time_text"],
                ser["data_type_label"],
                self._get_doses_str(doses),
                self._get_dose_units(doses),
                ser["response_units"],
                ser["expected_adversity_direction"],
                ser["percentControlMaxChange"],
            ]

            # dose-group specific information
            if len(ser["groups"]) > 1:
                row.extend(
                    [
                        self._get_dose(doses, 1),  # first non-zero dose
                        self._get_dose(doses, len(ser["groups"]) - 1),
                        self._get_dose(doses, ser["NOEL"]),
                        self._get_dose(doses, ser["LOEL"]),
                        self._get_dose(doses, ser["FEL"]),
                    ]
                )
            else:
                row.extend([None] * 5)

            row.extend([ser["trend_value"], ser["trend_result"]])

            # endpoint-group information
            for i, eg in enumerate(ser["groups"]):
                row_copy = copy(row)
                row_copy.extend(
                    [
                        eg["id"],
                        eg["dose_group_id"],
                        self._get_dose(doses, i),
                        eg["n"],
                        eg["incidence"],
                        eg["response"],
                        eg["stdev"],
                        eg["lower_ci"],
                        eg["upper_ci"],
                        eg["significant"],
                        eg["significance_level"],
                        eg["treatment_effect"],
                        eg["percentControlMean"],
                        eg["percentControlLow"],
                        eg["percentControlHigh"],
                        eg["dichotomous_summary"],
                        eg["percent_affected"],
                        eg["percent_lower_ci"],
                        eg["percent_upper_ci"],
                    ]
                )
                row_copy.extend(endpoint_robs)
                rows.append(row_copy)

        return rows


class EndpointFlatDataPivot(EndpointGroupFlatDataPivot):
    def _get_header_row(self):
        if self.queryset.first() is None:
            self.rob_headers, self.rob_data = {}, {}
        else:
            endpoint_ids = set(self.queryset.values_list("id", flat=True))
            self.rob_headers, self.rob_data = FinalRiskOfBiasScore.get_dp_export(
                self.queryset.first().assessment_id,
                endpoint_ids,
                "animal",
            )

        noel_names = self.kwargs["assessment"].get_noel_names()
        header = [
            "study id",
            "study name",
            "study identifier",
            "study published",
            "experiment id",
            "experiment name",
            "chemical",
            "animal group id",
            "animal group name",
            "lifestage exposed",
            "lifestage assessed",
            "species",
            "species strain",
            "generation",
            "animal description",
            "animal description (with N)",
            "sex",
            "route",
            "treatment period",
            "duration exposure",
            "duration exposure (days)",
            "endpoint id",
            "endpoint name",
            "system",
            "organ",
            "effect",
            "effect subtype",
            "diagnostic",
            "tags",
            "observation time",
            "observation time text",
            "data type",
            "doses",
            "dose units",
            "response units",
            "expected adversity direction",
            "low_dose",
            "high_dose",
            noel_names.noel,
            noel_names.loel,
            "FEL",
            "BMD",
            "BMDL",
            "trend test value",
            "trend test result",
        ]

        num_doses = self.queryset.model.max_dose_count(self.queryset)
        rng = range(1, num_doses + 1)
        header.extend([f"Dose {i}" for i in rng])
        header.extend([f"Significant {i}" for i in rng])
        header.extend([f"Treatment Related Effect {i}" for i in rng])
        header.extend(list(self.rob_headers.values()))

        # distinct applied last so that queryset can add annotations above
        # in self.queryset.model.max_dose_count
        self.queryset = self.queryset.distinct("pk")
        self.num_doses = num_doses

        return header

    @staticmethod
    def _get_bmd_values(bmds, preferred_units):
        # only return BMD values if they're in the preferred units
        for bmd in bmds:
            # return first match
            if bmd["dose_units_id"] in preferred_units and bmd["model"] is not None:
                return [bmd["bmd"], bmd["bmdl"]]
        return [None, None]

    @staticmethod
    def _dose_is_reported(dose_group_id: int, groups: list[dict]) -> bool:
        """
        Check if any numerical data( n, response, or incidence) was entered for a dose-group
        """
        for group in groups:
            if group["dose_group_id"] == dose_group_id:
                return any(group.get(key) is not None for key in ["n", "response", "incidence"])
        return False

    @staticmethod
    def _dose_low_high(dose_list: list[float | None]) -> tuple[float | None, float | None]:
        """
        Finds the lowest and highest non-zero dose from a given list of doses,
        ignoring None values. If there are no valid doses, returns None for both
        lowest and highest dose.

        Args:
            dose_list (list[Optional[float]]): List of doses

        Returns:
            tuple[Optional[float], Optional[float]]: Lowest dose and highest dose,
            in that order.
        """
        try:
            # map dose list to whether there is recorded data (valid)
            dose_validity_list = list(map(lambda d: d is not None, dose_list))
            # first valid dose
            low_index = dose_validity_list[1:].index(True) + 1
            # last valid dose
            high_index = len(dose_list) - 1 - dose_validity_list[1:][::-1].index(True)
            return (dose_list[low_index], dose_list[high_index])
        except ValueError:
            return (None, None)

    def _get_data_rows(self):
        preferred_units = self.kwargs.get("preferred_units", None)

        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            doses = self._get_doses_list(ser, preferred_units)

            # filter dose groups by those with recorded data
            filtered_doses = list(
                filter(lambda d: self._dose_is_reported(d["dose_group_id"], ser["groups"]), doses)
            )
            # special case - if no data was reported for any dose-group show all doses;
            # it may be the case that data wasn't extracted
            if len(filtered_doses) == 0:
                filtered_doses = doses

            # build endpoint-group independent data
            row = [
                ser["animal_group"]["experiment"]["study"]["id"],
                ser["animal_group"]["experiment"]["study"]["short_citation"],
                ser["animal_group"]["experiment"]["study"]["study_identifier"],
                ser["animal_group"]["experiment"]["study"]["published"],
                ser["animal_group"]["experiment"]["id"],
                ser["animal_group"]["experiment"]["name"],
                ser["animal_group"]["experiment"]["chemical"],
                ser["animal_group"]["id"],
                ser["animal_group"]["name"],
                ser["animal_group"]["lifestage_exposed"],
                ser["animal_group"]["lifestage_assessed"],
                ser["animal_group"]["species"],
                self._get_species_strain(ser),
                ser["animal_group"]["generation"],
                get_gen_species_strain_sex(ser, withN=False),
                get_gen_species_strain_sex(ser, withN=True),
                ser["animal_group"]["sex"],
                ser["animal_group"]["dosing_regime"]["route_of_exposure"].lower(),
                get_treatment_period(
                    ser["animal_group"]["experiment"],
                    ser["animal_group"]["dosing_regime"],
                ),
                ser["animal_group"]["dosing_regime"]["duration_exposure_text"],
                ser["animal_group"]["dosing_regime"]["duration_exposure"],
                ser["id"],
                ser["name"],
                ser["system"],
                ser["organ"],
                ser["effect"],
                ser["effect_subtype"],
                ser["diagnostic"],
                self.get_flattened_tags(ser, "effects"),
                self._get_observation_time_and_time_units(ser),
                ser["observation_time_text"],
                ser["data_type_label"],
                self._get_doses_str(filtered_doses),
                self._get_dose_units(doses),
                ser["response_units"],
                ser["expected_adversity_direction"],
            ]

            # if groups exist, pull all available. Otherwise, start with an empty list. This
            # is preferred than just pulling in edge cases where an endpoint has no data
            # extracted but has more dose-groups at the animal group level than are avaiable
            # for the entire data export. For example, an endpoint may have no data extracted
            # and dose-groups, but the entire export may only have data with 4 dose-groups.
            dose_list = (
                [
                    self._get_dose(doses, i) if self._dose_is_reported(i, ser["groups"]) else None
                    for i in range(len(doses))
                ]
                if ser["groups"]
                else []
            )

            # dose-group specific information
            row.extend(self._dose_low_high(dose_list))
            try:
                row.append(dose_list[ser["NOEL"]])
            except IndexError:
                row.append(None)
            try:
                row.append(dose_list[ser["LOEL"]])
            except IndexError:
                row.append(None)
            try:
                row.append(dose_list[ser["FEL"]])
            except IndexError:
                row.append(None)

            dose_list.extend([None] * (self.num_doses - len(dose_list)))

            # bmd/bmdl information
            row.extend(self._get_bmd_values(ser["bmds"], preferred_units))

            row.extend([ser["trend_value"], ser["trend_result"]])

            row.extend(dose_list)

            sigs = get_significance_and_direction(ser["data_type"], ser["groups"])
            sigs.extend([None] * (self.num_doses - len(sigs)))
            row.extend(sigs)

            tres = [dose["treatment_effect"] for dose in ser["groups"]]
            tres.extend([None] * (self.num_doses - len(tres)))
            row.extend(tres)

            row.extend(
                [self.rob_data[(ser["id"], metric_id)] for metric_id in self.rob_headers.keys()]
            )

            rows.append(row)

        return rows


class EndpointSummary(FlatFileExporter):
    def _get_header_row(self):
        return [
            "study-short_citation",
            "study-study_identifier",
            "experiment-chemical",
            "animal_group-name",
            "animal_group-sex",
            "animal description (with n)",
            "dosing_regime-route_of_exposure",
            "dosing_regime-duration_exposure_text",
            "species-name",
            "strain-name",
            "endpoint-id",
            "endpoint-url",
            "endpoint-system",
            "endpoint-organ",
            "endpoint-effect",
            "endpoint-name",
            "endpoint-observation_time",
            "endpoint-response_units",
            "Dose units",
            "Doses",
            "N",
            "Responses",
            "Doses and responses",
            "Response direction",
        ]

    def _get_data_rows(self):
        def getDoseUnits(doses):
            return set(sorted([d["dose_units"]["name"] for d in doses]))

        def getDoses(doses, unit):
            doses = [d["dose"] for d in doses if d["dose_units"]["name"] == unit]
            return [f"{d:g}" for d in doses]

        def getNs(groups):
            return [f"{grp['n'] if grp['n'] is not None else ''}" for grp in groups]

        def getResponses(groups):
            resps = []
            for grp in groups:
                txt = ""
                if grp["isReported"]:
                    if grp["response"] is not None:
                        txt = f"{grp['response']:g}"
                    else:
                        txt = f"{grp['incidence']:g}"
                    if grp["variance"] is not None:
                        txt = f"{txt} ± {grp['variance']:g}"
                resps.append(txt)
            return resps

        def getDR(doses, responses, units):
            txts = []
            for i in range(len(doses)):
                if len(responses) > i and len(responses[i]) > 0:
                    txt = f"{doses[i]} {units}: {responses[i]}"
                    txts.append(txt)
            return ", ".join(txts)

        def getResponseDirection(responses, data_type):
            # return unknown if control response is null
            if responses and responses[0]["response"] is None:
                return "?"

            txt = "↔"
            for resp in responses:
                if resp["significant"]:
                    if data_type in ["C", "P"]:
                        if resp["response"] > responses[0]["response"]:
                            txt = "↑"
                        else:
                            txt = "↓"
                    else:
                        txt = "↑"
                    break
            return txt

        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)

            doses = ser["animal_group"]["dosing_regime"]["doses"]
            units = getDoseUnits(doses)

            # build endpoint-group independent data
            row = [
                ser["animal_group"]["experiment"]["study"]["short_citation"],
                ser["animal_group"]["experiment"]["study"]["study_identifier"],
                ser["animal_group"]["experiment"]["chemical"],
                ser["animal_group"]["name"],
                ser["animal_group"]["sex"],
                get_gen_species_strain_sex(ser, withN=True),
                ser["animal_group"]["dosing_regime"]["route_of_exposure"],
                get_treatment_period(
                    ser["animal_group"]["experiment"],
                    ser["animal_group"]["dosing_regime"],
                ),
                ser["animal_group"]["species"],
                ser["animal_group"]["strain"],
                ser["id"],
                ser["url"],
                ser["system"],
                ser["organ"],
                ser["effect"],
                ser["name"],
                ser["observation_time_text"],
                ser["response_units"],
            ]

            responses_list = getResponses(ser["groups"])
            ns_list = getNs(ser["groups"])
            response_direction = getResponseDirection(ser["groups"], ser["data_type"])
            for unit in units:
                row_copy = copy(row)
                doses_list = getDoses(doses, unit)
                row_copy.extend(
                    [
                        unit,  # 'units'
                        ", ".join(doses_list),  # Doses
                        ", ".join(ns_list),  # Ns
                        ", ".join(responses_list),  # Responses w/ units
                        getDR(doses_list, responses_list, unit),
                        response_direction,
                    ]
                )
                rows.append(row_copy)

        return rows
