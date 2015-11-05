from study.models import Study
from utils.helper import FlatFileExporter

from . import models


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
            row.extend(Study.flat_complete_data_row(ser['study_population']['study']))
            row.extend(models.StudyPopulation.flat_complete_data_row(ser['study_population']))
            row.extend(models.Outcome.flat_complete_data_row(ser))
            for res in ser['results']:
                row_copy = list(row)
                row_copy.extend(models.Exposure.flat_complete_data_row(res["comparison_set"]["exposure"]))
                row_copy.extend(models.ComparisonSet.flat_complete_data_row(res["comparison_set"]))
                row_copy.extend(models.Result.flat_complete_data_row(res))
                for rg in res['results']:
                    row_copy2 = list(row_copy)
                    row_copy2.extend(models.Group.flat_complete_data_row(rg["group"]))
                    row_copy2.extend(models.GroupResult.flat_complete_data_row(rg))
                    rows.append(row_copy2)
        return rows


class OutcomeDataPivot(FlatFileExporter):

    def _get_header_row(self):
        return [
            'study id',
            'study name',
            'study published',

            'study population id',
            'study population name',
            'design',

            'outcome id',
            'outcome name',
            'outcome effect subtype',
            'diagnostic',
            'age of outcome measurement',

            'comparison set id',
            'comparison set name',

            'exposure id',
            'exposure name',
            'exposure metric',
            'exposure measured',
            'dose units',
            'age of exposure',

            'result id',
            'result population description',
            'statistical metric',
            'statistical metric abbreviation',
            'statistical metric description',
            'result summary',
            'dose response',
            'statistical power',
            'CI units',

            'exposure group order',
            'exposure group name',
            'exposure group comparison name',
            'exposure group numeric',

            'key',
            'result group id',
            'N',
            'estimate',
            'lower CI',
            'upper CI',
            'variance',
            'statistical significance',
            'statistical significance (numeric)',
            'main finding',
            'main finding support',
        ]

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = [
                ser['study_population']['study']['id'],
                ser['study_population']['study']['short_citation'],
                ser['study_population']['study']['published'],

                ser['study_population']['id'],
                ser['study_population']['name'],
                ser['study_population']['design'],

                ser['id'],
                ser['name'],
                ser['effect_subtype'],
                ser['diagnostic'],
                ser['age_of_measurement'],
            ]
            for res in ser['results']:
                row_copy = list(row)
                row_copy.extend([
                    res["comparison_set"]["id"],
                    res["comparison_set"]["name"],

                    res["comparison_set"]["exposure"]["id"],
                    res["comparison_set"]["exposure"]["name"],
                    res["comparison_set"]["exposure"]["metric"],
                    res["comparison_set"]["exposure"]["measured"],
                    res["comparison_set"]["exposure"]["metric_units"]["name"],
                    res["comparison_set"]["exposure"]["age_of_exposure"],

                    res['id'],
                    res['population_description'],
                    res['metric']['metric'],
                    res['metric']['abbreviation'],
                    res['metric_description'],
                    res['comments'],
                    res['dose_response'],
                    res['statistical_power'],
                    res['ci_units'],
                ])
                for rg in res['results']:
                    row_copy2 = list(row_copy)
                    row_copy2.extend([
                        rg['group']['group_id'],
                        rg['group']['name'],
                        rg['group']['comparative_name'],
                        rg['group']['numeric'],

                        rg['id'],
                        rg['id'],  # repeat for data-pivot key
                        rg['n'],
                        rg['estimate'],
                        rg['lower_ci'],
                        rg['upper_ci'],
                        rg['variance'],
                        rg['p_value_text'],
                        rg['p_value'],
                        rg['is_main_finding'],
                        rg['main_finding_support'],
                    ])
                    rows.append(row_copy2)
        return rows
