import math

import pandas as pd
from django.db.models import Exists, OuterRef, F
from django.db.models.lookups import Exact


from ..common.exports import Exporter, ModelExport
from ..common.helper import FlatFileExporter
from ..common.models import sql_display, str_m2m, sql_format
from ..materialized.models import FinalRiskOfBiasScore
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


class ExperimentExport(ModelExport):
    # experiment
    def get_value_map(self):
        return {
            "id":"id",
            "url":"url",
            "name":"name",
            "type":"type",
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
            "url": sql_format("/epi/study-population/{}/", query_prefix + "id"),  # hardcoded URL
        }

class AnimalGroupExport(ModelExport):
    # animal_group
    def get_value_map(self):
        return {
            "id":"id",
            "url":"url",
            "name":"name",
            "sex":"sex",
            "animal_source":"animal_source",
            "lifestage_exposed":"lifestage_exposed",
            "lifestage_assessed":"lifestage_assessed",
            "siblings":"siblings",
            "parents":"parents",
            "generation":"generation",
            "comments":"comments",
            "diet":"diet",
            "species":"species",
            "strain":"strain",
        }
    def get_annotation_map(self, query_prefix):
        return {
            "url": sql_format("/epi/study-population/{}/", query_prefix + "id"),  # hardcoded URL
        }


class DosingRegimeExport(ModelExport):
    # dosing_regime
    def get_value_map(self):
        return {
            "id":"id",
            "dosed_animals":"dosed_animals",
            "route_of_exposure":"route_of_exposure",
            "duration_exposure":"duration_exposure",
            "duration_exposure_text":"duration_exposure_text",
            "duration_observation":"duration_observation",
            "num_dose_groups":"num_dose_groups",
            "positive_control":"positive_control",
            "negative_control":"negative_control",
            "description":"description",
        }



class EndpointExport(ModelExport):
    # endpoint
    def get_value_map(self):
        return {
            "id":"id",
            "url":"url",
            "name":"name",
            "effects":"effects",
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
            "observation_time_units":"observation_time_units",
            "observation_time_text":"observation_time_text",
            "data_location":"data_location",
            "response_units":"response_units",
            "data_type":"data_type",
            "variance_type":"variance_type",
            "confidence_interval":"confidence_interval",
            "data_reported":"data_reported",
            "data_extracted":"data_extracted",
            "values_estimated":"values_estimated",
            "expected_adversity_direction":"expected_adversity_direction",
            "monotonicity":"monotonicity",
            "statistical_test":"statistical_test",
            "trend_value":"trend_value",
            "trend_result":"trend_result",
            "diagnostic":"diagnostic",
            "power_notes":"power_notes",
            "results_notes":"results_notes",
            "endpoint_notes":"endpoint_notes",
            "additional_fields":"additional_fields",
        }

    def get_annotation_map(self, query_prefix):
        return {
            "url": sql_format("/epi/study-population/{}/", query_prefix + "id"),  # hardcoded URL
        }


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
        ]

### FIRST
class EndpointGroupFlatComplete2(FlatFileExporter):
    # add flat doses, otherwise good?
    def build_df(self) -> pd.DataFrame:
        df = AnimalExporter().get_df(
            self.queryset.select_related(
                "animal_group__experiment__study", "animal_group__dosing_regime",
            )
            .prefetch_related("groups",)
            .order_by("id", "groups",)
        )

        return df

### SECOND
class EndpointGroupFlatDataPivot2(FlatFileExporter):

    def build_df(self) -> pd.DataFrame:
        df = AnimalExporter().get_df(
            self.queryset.select_related(
                "animal_group__experiment__study", "animal_group__dosing_regime",
            )
            .prefetch_related("groups",)
            .order_by("id", "groups",)
        )

        df = df.rename(
            columns={
                "study-id": "study id",
                "study-short_citation": "study name",
                "study-study_identifier": "study identifier",
                "study-published": "study published",
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
