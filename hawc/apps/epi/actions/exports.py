from ...common.helper import FlatFileExporter
from ...materialized.models import FinalRiskOfBiasScore
from ...study.models import Study
from .. import models


class OutcomeComplete(FlatFileExporter):
    def _get_header_row(self):
        header = []
        header.extend(Study.flat_complete_header_row())
        header.extend(models.StudyPopulation.flat_complete_header_row())
        header.extend(models.Outcome.flat_complete_header_row())
        header.extend(models.Exposure.flat_complete_header_row())
        header.extend(models.ComparisonSet.flat_complete_header_row())
        header.extend(models.Result.flat_complete_header_row())
        header.extend(models.Group.flat_complete_header_row())
        header.extend(models.GroupResult.flat_complete_header_row())
        return header

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = []
            row.extend(Study.flat_complete_data_row(ser["study_population"]["study"]))
            row.extend(models.StudyPopulation.flat_complete_data_row(ser["study_population"]))
            row.extend(models.Outcome.flat_complete_data_row(ser))
            for res in ser["results"]:
                row_copy = list(row)
                row_copy.extend(
                    models.Exposure.flat_complete_data_row(res["comparison_set"]["exposure"])
                )
                row_copy.extend(models.ComparisonSet.flat_complete_data_row(res["comparison_set"]))
                row_copy.extend(models.Result.flat_complete_data_row(res))
                for rg in res["results"]:
                    row_copy2 = list(row_copy)
                    row_copy2.extend(models.Group.flat_complete_data_row(rg["group"]))
                    row_copy2.extend(models.GroupResult.flat_complete_data_row(rg))
                    rows.append(row_copy2)
        return rows


class OutcomeDataPivot(FlatFileExporter):
    def _get_header_row(self):
        if self.queryset.first() is None:
            self.rob_headers, self.rob_data = {}, {}
        else:
            outcome_ids = set(self.queryset.values_list("id", flat=True))
            self.rob_headers, self.rob_data = FinalRiskOfBiasScore.get_dp_export(
                self.queryset.first().assessment_id, outcome_ids, "epi",
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
