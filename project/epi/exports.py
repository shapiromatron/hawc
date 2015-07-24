from study.models import Study
from utils.helper import FlatFileExporter
from . import models


class AssessedOutcomeFlatComplete(FlatFileExporter):
    """
    Returns a complete export of all data required to rebuild the the
    epidemiological study type from scratch.
    """

    def _get_header_row(self):
        header = []
        header.extend(Study.flat_complete_header_row())
        header.extend(models.StudyPopulation.flat_complete_header_row())
        header.extend(models.Exposure.flat_complete_header_row())
        header.extend(models.AssessedOutcome.flat_complete_header_row())
        header.extend(models.AssessedOutcomeGroup.flat_complete_header_row())
        return header

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = []
            row.extend(Study.flat_complete_data_row(ser['exposure']['study_population']['study']))
            row.extend(models.StudyPopulation.flat_complete_data_row(ser['exposure']['study_population']))
            row.extend(models.Exposure.flat_complete_data_row(ser['exposure']))
            row.extend(models.AssessedOutcome.flat_complete_data_row(ser))
            # build a row for each aog
            for aog in ser['groups']:
                row_copy = list(row)  # clone
                row_copy.extend(models.AssessedOutcomeGroup.flat_complete_data_row(aog))
                rows.append(row_copy)
        return rows


class AssessedOutcomeFlatDataPivot(FlatFileExporter):
    """
    Return a subset of frequently-used data for generation of data-pivot
    visualizations.
    """

    def _get_header_row(self):
        return [
            'Study',
            'Study URL',
            'Study HAWC ID',
            'Study Published?',

            'Study Population Name',
            'Study Population Key',
            'Design',
            'Study Population URL',

            'Exposure',
            'Exposure Key',
            'Exposure Metric',
            'Exposure URL',
            'Dose Units',

            'Assessed Outcome Name',
            'Assessed Outcome Population Description',
            'Assessed Outcome Key',
            'Diagnostic',
            'Statistical Metric',
            'Statistical Metric Abbreviation',
            'Statistical Metric Description',
            'Outcome Summary',
            'Dose Response',
            'Statistical Power',
            'Support Main Finding',

            'Exposure Group Name',
            'Exposure Group Comparative Description Name',
            'Exposure Group Order',
            'Exposure Group Numeric',

            'Row Key',
            'Assessed Outcome Group Primary Key',
            'N',
            'Estimate',
            'Lower CI',
            'Upper CI',
            'CI units',
            'SE',
            'Statistical Significance',
            'Statistical Significance (numeric)',
            'Main Finding'
        ]

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)

            row = [
                ser['exposure']['study_population']['study']['short_citation'],
                ser['exposure']['study_population']['study']['url'],
                ser['exposure']['study_population']['study']['id'],
                ser['exposure']['study_population']['study']['published'],

                ser['exposure']['study_population']['name'],
                ser['exposure']['study_population']['id'],
                ser['exposure']['study_population']['design'],
                ser['exposure']['study_population']['url'],

                ser['exposure']['exposure_form_definition'],
                ser['exposure']['id'],
                ser['exposure']['metric'],
                ser['exposure']['url'],
                ser['exposure']['metric_units']['name'],

                ser['name'],
                ser['population_description'],
                ser['id'],
                ser['diagnostic'],
                ser['statistical_metric']['metric'],
                ser['statistical_metric']['abbreviation'],
                ser['statistical_metric_description'],
                ser['summary'],
                ser['dose_response'],
                ser['statistical_power'],
                ser['main_finding_support'],
            ]

            for group in ser['groups']:
                row_copy = list(row)  # clone
                row_copy.extend([
                    group['exposure_group']['description'],
                    group['exposure_group']['comparative_name'],
                    group['exposure_group']['exposure_group_id'],
                    group['exposure_group']['exposure_numeric'],

                    group['id'], # repeat for data-pivot key
                    group['id'],
                    group['n'],
                    group['estimate'],
                    group['lower_ci'],
                    group['upper_ci'],
                    group['ci_units'],
                    group['se'],
                    group['p_value_text'],
                    group['p_value'],
                    group['isMainFinding']
                ])
                rows.append(row_copy)

        return rows


class MetaResultFlatComplete(FlatFileExporter):
    """
    Returns a complete export of all data required to rebuild the the
    epidemiological meta-result study type from scratch.
    """

    def _get_header_row(self):
        header = []
        header.extend(Study.flat_complete_header_row())
        header.extend(models.MetaProtocol.flat_complete_header_row())
        header.extend(models.MetaResult.flat_complete_header_row())
        header.extend(models.SingleResult.flat_complete_header_row())
        return header

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = []
            row.extend(Study.flat_complete_data_row(ser['protocol']['study']))
            row.extend(models.MetaProtocol.flat_complete_data_row(ser['protocol']))
            row.extend(models.MetaResult.flat_complete_data_row(ser))

            if len(ser['single_results'])==0:
                # print one-row with no single-results
                rows.append(row)
            else:
                # print each single-result as a new row
                for sr in ser['single_results']:
                    row_copy = list(row)  # clone
                    row_copy.extend(models.SingleResult.flat_complete_data_row(sr))
                    rows.append(row_copy)
        return rows


class MetaResultFlatDataPivot(FlatFileExporter):
    """
    Return a subset of frequently-used data for generation of data-pivot
    visualizations.
    """

    def _get_header_row(self):
        return [
            'Study',
            'Study URL',
            'Study HAWC ID',
            'Study Published?',

            'Protocol Primary Key',
            'Protocol URL',
            'Protocol Name',
            'Protocol Type',
            'Total References',
            'Identified References',

            'Row Key',
            'Result Primary Key',
            'Result URL',
            'Result Label',
            'Health Outcome',
            'Exposure',
            'Result References',
            'Statistical Metric',
            'Statistical Metric Abbreviation',
            'N',
            'Estimate',
            'Lower CI',
            'Upper CI',
            'CI units',
            'Heterogeneity'
        ]

    def _get_data_rows(self):
        rows = []
        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            row = [
                ser['protocol']['study']['short_citation'],
                ser['protocol']['study']['url'],
                ser['protocol']['study']['id'],
                ser['protocol']['study']['published'],

                ser['protocol']['id'],
                ser['protocol']['url'],
                ser['protocol']['name'],
                ser['protocol']['protocol_type'],
                ser['protocol']['total_references'],
                ser['protocol']['total_studies_identified'],

                ser['id'],  # repeat for data-pivot key
                ser['id'],
                ser['url'],
                ser['label'],
                ser['health_outcome'],
                ser['exposure_name'],
                ser['number_studies'],
                ser['statistical_metric']['metric'],
                ser['statistical_metric']['abbreviation'],
                ser['n'],
                ser['estimate'],
                ser['lower_ci'],
                ser['upper_ci'],
                ser['ci_units'],
                ser['heterogeneity'],
            ]
            rows.append(row)

        return rows
