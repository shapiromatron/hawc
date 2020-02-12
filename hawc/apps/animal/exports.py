from copy import copy

from ..assessment.models import DoseUnits
from ..common.helper import FlatFileExporter
from ..riskofbias.models import RiskOfBias
from ..study.models import Study
from . import models


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

    if data_type == models.Endpoint.DATA_TYPE_CONTINUOUS:
        control_resp = groups[0]["response"]
        for group in groups:
            if group["significant"]:
                resp = group["response"]
                if control_resp is None or resp is None or resp == control_resp:
                    significance_list.append("Yes - ?")
                elif resp > control_resp:
                    significance_list.append("Yes - ↑")
                else:
                    significance_list.append("Yes - ↓")
            else:
                significance_list.append("No")
    elif data_type in [
        models.Endpoint.DATA_TYPE_DICHOTOMOUS,
        models.Endpoint.DATA_TYPE_DICHOTOMOUS_CANCER,
    ]:
        for group in groups:
            if group["significant"]:
                significance_list.append("Yes - ↑")
            else:
                significance_list.append("No")
    elif data_type == models.Endpoint.DATA_TYPE_PERCENT_DIFFERENCE:
        for group in groups:
            if group["significant"]:
                resp = group["response"]
                if resp is None or resp == 0:
                    significance_list.append("Yes - ?")
                elif resp > 0:
                    significance_list.append("Yes - ↑")
                else:
                    significance_list.append("Yes - ↓")
            else:
                significance_list.append("No")
    else:
        raise ValueError("Unknown state to determine significance/direction")

    return significance_list


class EndpointGroupFlatComplete(FlatFileExporter):
    """
    Returns a complete export of all data required to rebuild the the
    animal bioassay study type from scratch.
    """

    def _get_header_row(self):
        self.doses = DoseUnits.objects.get_animal_units(self.kwargs.get("assessment"))

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
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = []
            row.extend(Study.flat_complete_data_row(ser["animal_group"]["experiment"]["study"]))
            row.extend(models.Experiment.flat_complete_data_row(ser["animal_group"]["experiment"]))
            row.extend(models.AnimalGroup.flat_complete_data_row(ser["animal_group"]))
            row.extend(
                models.DosingRegime.flat_complete_data_row(ser["animal_group"]["dosing_regime"])
            )
            row.extend(models.Endpoint.flat_complete_data_row(ser))
            for i, eg in enumerate(ser["groups"]):
                row_copy = copy(row)
                row_copy.extend(
                    models.DoseGroup.flat_complete_data_row(
                        ser["animal_group"]["dosing_regime"]["doses"], self.doses, i
                    )
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
    def _get_dose_units(cls, doses):
        return doses[0]["dose_units"]["name"]

    @classmethod
    def _get_doses_str(cls, doses):
        values = ", ".join([str(float(d["dose"])) for d in doses])
        return f"{values} {cls._get_dose_units(doses)}"

    @classmethod
    def _get_dose(cls, doses, idx):
        for dose in doses:
            if dose["dose_group_id"] == idx:
                return float(dose["dose"])
        return None

    @classmethod
    def _get_species_strain(cls, e):
        return f"{e['animal_group']['species']} {e['animal_group']['strain']}"

    @classmethod
    def _get_tags(cls, e):
        effs = [tag["name"] for tag in e["effects"]]
        if len(effs) > 0:
            return f"|{'|'.join(effs)}|"
        return ""

    @classmethod
    def _get_observation_time_and_time_units(cls, e):
        return f"{e['observation_time']} {e['observation_time_units']}"

    def _get_header_row(self):
        # move qs.distinct() call here so we can make qs annotations.
        self.queryset = self.queryset.distinct("pk")
        if self.queryset.first() is None:
            self.rob_headers, self.rob_data = {}, {}
        else:
            self.rob_headers, self.rob_data = RiskOfBias.get_dp_export(
                self.queryset.first().assessment_id,
                list(
                    self.queryset.values_list(
                        "animal_group__experiment__study_id", flat=True
                    ).distinct()
                ),
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
            noel_names.noel,
            noel_names.loel,
            "FEL",
            "high_dose",
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
            study_id = ser["animal_group"]["experiment"]["study"]["id"]
            study_robs = [
                self.rob_data[(study_id, metric_id)] for metric_id in self.rob_headers.keys()
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
                    ser["animal_group"]["experiment"], ser["animal_group"]["dosing_regime"],
                ),
                ser["animal_group"]["dosing_regime"]["duration_exposure_text"],
                ser["id"],
                ser["name"],
                ser["system"],
                ser["organ"],
                ser["effect"],
                ser["effect_subtype"],
                ser["diagnostic"],
                self._get_tags(ser),
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
                        self._get_dose(doses, ser["NOEL"]),
                        self._get_dose(doses, ser["LOEL"]),
                        self._get_dose(doses, ser["FEL"]),
                        self._get_dose(doses, len(ser["groups"]) - 1),
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
                        eg["percentControlMean"],
                        eg["percentControlLow"],
                        eg["percentControlHigh"],
                        eg["dichotomous_summary"],
                        eg["percent_affected"],
                        eg["percent_lower_ci"],
                        eg["percent_upper_ci"],
                    ]
                )
                row_copy.extend(study_robs)
                rows.append(row_copy)

        return rows


class EndpointFlatDataPivot(EndpointGroupFlatDataPivot):
    def _get_header_row(self):
        if self.queryset.first() is None:
            self.rob_headers, self.rob_data = {}, {}
        else:
            self.rob_headers, self.rob_data = RiskOfBias.get_dp_export(
                self.queryset.first().assessment_id,
                list(
                    self.queryset.values_list(
                        "animal_group__experiment__study_id", flat=True
                    ).distinct()
                ),
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
            noel_names.noel,
            noel_names.loel,
            "FEL",
            "high_dose",
            "BMD",
            "BMDL",
            "trend test value",
            "trend test result",
        ]

        num_doses = self.queryset.model.max_dose_count(self.queryset)
        rng = range(1, num_doses + 1)
        header.extend([f"Dose {i}" for i in rng])
        header.extend([f"Significant {i}" for i in rng])
        header.extend(list(self.rob_headers.values()))

        # distinct applied last so that queryset can add annotations above
        # in self.queryset.model.max_dose_count
        self.queryset = self.queryset.distinct("pk")
        self.num_doses = num_doses

        return header

    @staticmethod
    def _get_bmd_values(bmd, preferred_units):
        # only return BMD values if they're in the preferred units
        if bmd and bmd["dose_units"] in preferred_units:
            return [bmd["output"]["BMD"], bmd["output"]["BMDL"]]
        return [None, None]

    def _get_data_rows(self):

        preferred_units = self.kwargs.get("preferred_units", None)

        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            doses = self._get_doses_list(ser, preferred_units)

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
                    ser["animal_group"]["experiment"], ser["animal_group"]["dosing_regime"],
                ),
                ser["animal_group"]["dosing_regime"]["duration_exposure_text"],
                ser["id"],
                ser["name"],
                ser["system"],
                ser["organ"],
                ser["effect"],
                ser["effect_subtype"],
                ser["diagnostic"],
                self._get_tags(ser),
                self._get_observation_time_and_time_units(ser),
                ser["observation_time_text"],
                ser["data_type_label"],
                self._get_doses_str(doses),
                self._get_dose_units(doses),
                ser["response_units"],
                ser["expected_adversity_direction"],
            ]

            # dose-group specific information
            if len(ser["groups"]) > 1:
                row.extend(
                    [
                        self._get_dose(doses, 1),  # first non-zero dose
                        self._get_dose(doses, ser["NOEL"]),
                        self._get_dose(doses, ser["LOEL"]),
                        self._get_dose(doses, ser["FEL"]),
                        self._get_dose(doses, len(ser["groups"]) - 1),
                    ]
                )
            else:
                row.extend([None] * 5)

            # bmd/bmdl information
            row.extend(self._get_bmd_values(ser["bmd"], preferred_units))

            row.extend([ser["trend_value"], ser["trend_result"]])

            dose_list = [self._get_dose(doses, i) for i in range(len(doses))]
            sigs = get_significance_and_direction(ser["data_type"], ser["groups"])

            dose_list.extend([None] * (self.num_doses - len(dose_list)))
            sigs.extend([None] * (self.num_doses - len(sigs)))

            row.extend(dose_list)
            row.extend(sigs)

            study_id = ser["animal_group"]["experiment"]["study"]["id"]
            row.extend(
                [self.rob_data[(study_id, metric_id)] for metric_id in self.rob_headers.keys()]
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
                    ser["animal_group"]["experiment"], ser["animal_group"]["dosing_regime"],
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

            responsesList = getResponses(ser["groups"])
            responseDirection = getResponseDirection(ser["groups"], ser["data_type"])
            for unit in units:
                row_copy = copy(row)
                dosesList = getDoses(doses, unit)
                row_copy.extend(
                    [
                        unit,  # 'units'
                        ", ".join(dosesList),  # Doses
                        ", ".join(responsesList),  # Responses w/ units
                        getDR(dosesList, responsesList, unit),
                        responseDirection,
                    ]
                )
                rows.append(row_copy)

        return rows
