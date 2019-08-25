from copy import copy
from django.apps import apps

from animal.exports import get_final_rob_text
from utils.helper import FlatFileExporter


def getDose(ser, tag):
    if ser[tag] != -999:
        return ser['groups'][ser[tag]]['dose']
    else:
        return None


def getDoseRange(ser):
    # get non-zero dose range
    doses = [
        eg['dose'] for eg in ser['groups'] if eg['dose'] > 0
    ]
    if doses:
        return min(doses), max(doses)
    else:
        return None, None


class DataPivotEndpoint(FlatFileExporter):

    def _get_header_row(self):
        header = [
            'study id',
            'study name',
            'study identifier',
            'study published',

            'chemical id',
            'chemical name',
            'chemical CAS',
            'chemical purity',

            'IVExperiment id',
            'IVCellType id',
            'cell species',
            'cell strain',
            'cell sex',
            'cell type',
            'cell tissue',

            'Dose units',
            'Metabolic activation',
            'Transfection',

            'key',
            'IVEndpoint id',
            'IVEndpoint name',
            'IVEndpoint description tags',
            'assay type',
            'endpoint description',
            'endpoint response units',
            'observation time',
            'observation time units',
            'NOEL',
            'LOEL',
            'monotonicity',
            'overall pattern',
            'trend test result',
            'minimum dose',
            'maximum dose',
            'number of doses',
            'Overall study confidence'
        ]

        num_cats = 0
        if self.queryset.count() > 0:
            IVEndpointCategory = apps.get_model("invitro", "IVEndpointCategory")
            num_cats = IVEndpointCategory.get_maximum_depth(
                self.queryset[0].assessment_id)
        header.extend([
            "Category {0}".format(i)
            for i in range(1, num_cats + 1)
        ])

        num_doses = self.queryset.model.max_dose_count(self.queryset)
        rng = range(1, num_doses + 1)
        header.extend(["Dose {0}".format(i) for i in rng])
        header.extend(["Change Control {0}".format(i) for i in rng])
        header.extend(["Significant {0}".format(i) for i in rng])
        header.extend(["Cytotoxicity {0}".format(i) for i in rng])

        num_bms = self.queryset.model.max_benchmark_count(self.queryset)
        rng = range(1, num_bms + 1)
        header.extend(["Benchmark Type {0}".format(i) for i in rng])
        header.extend(["Benchmark Value {0}".format(i) for i in rng])

        self.num_cats = num_cats
        self.num_doses = num_doses
        self.num_bms = num_bms

        return header

    def _get_data_rows(self):
        rows = []

        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)
            study_id = ser['experiment']['study']['id']
            finalROB = get_final_rob_text(study_id)

            doseRange = getDoseRange(ser)

            cats = ser['category']['names'] if ser["category"] else []

            doses = [eg['dose'] for eg in ser['groups']]
            diffs = [eg['difference_control'] for eg in ser['groups']]
            sigs = [eg['significant_control'] for eg in ser['groups']]
            cytotoxes = [eg['cytotoxicity_observed'] for eg in ser['groups']]

            if doses and doses[0] == 0:
                doses.pop(0)
                diffs.pop(0)
                sigs.pop(0)

            number_doses = len(doses)

            bm_types = [bm["benchmark"] for bm in ser["benchmarks"]]
            bm_values = [bm["value"] for bm in ser["benchmarks"]]

            row = [
                ser['experiment']['study']['id'],
                ser['experiment']['study']['short_citation'],
                ser['experiment']['study']['study_identifier'],
                ser['experiment']['study']['published'],

                ser['chemical']['id'],
                ser['chemical']['name'],
                ser['chemical']['cas'],
                ser['chemical']['purity'],

                ser['experiment']['id'],
                ser['experiment']['cell_type']['id'],
                ser['experiment']['cell_type']['species'],
                ser['experiment']['cell_type']['strain'],
                ser['experiment']['cell_type']['sex'],
                ser['experiment']['cell_type']['cell_type'],
                ser['experiment']['cell_type']['tissue'],

                ser['experiment']['dose_units']['name'],
                ser['experiment']['metabolic_activation'],
                ser['experiment']['transfection'],

                ser['id'],  # repeat for data-pivot key
                ser['id'],
                ser['name'],
                '|'.join([d['name'] for d in ser['effects']]),
                ser['assay_type'],
                ser['short_description'],
                ser['response_units'],
                ser['observation_time'],
                ser['observation_time_units'],
                getDose(ser, 'NOEL'),
                getDose(ser, 'LOEL'),
                ser['monotonicity'],
                ser['overall_pattern'],
                ser['trend_test'],
                doseRange[0],
                doseRange[1],
                number_doses,
                finalROB
            ]

            # extend rows to include blank placeholders, and apply
            cats.extend([None] * (self.num_cats-len(cats)))
            doses.extend([None] * (self.num_doses-len(doses)))
            diffs.extend([None] * (self.num_doses-len(diffs)))
            sigs.extend([None] * (self.num_doses-len(sigs)))
            cytotoxes.extend([None] * (self.num_doses-len(cytotoxes)))

            bm_types.extend([None] * (self.num_bms-len(bm_types)))
            bm_values.extend([None] * (self.num_bms-len(bm_values)))

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
        header = [
            'study id',
            'study name',
            'study identifier',
            'study published',

            'chemical id',
            'chemical name',
            'chemical CAS',
            'chemical purity',

            'IVExperiment id',
            'IVCellType id',
            'cell species',
            'cell strain',
            'cell sex',
            'cell type',
            'cell tissue',

            'dose units',
            'metabolic activation',
            'transfection',

            'IVEndpoint id',
            'IVEndpoint name',
            'IVEndpoint description tags',
            'assay type',
            'endpoint description',
            'endpoint response units',
            'observation time',
            'observation time units',
            'low_dose',
            'NOEL',
            'LOEL',
            'high_dose',
            'monotonicity',
            'overall pattern',
            'trend test result',

            'key',
            'dose index',
            'dose',
            'N',
            'response',
            'stdev',
            'percent control mean',
            'percent control low',
            'percent control high',
            'change from control',
            'significant from control',
            'cytotoxicity observed',
            'precipitation observed',
        ]
        return header

    def _get_data_rows(self):
        rows = []

        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)

            doseRange = getDoseRange(ser)

            row = [
                ser['experiment']['study']['id'],
                ser['experiment']['study']['short_citation'],
                ser['experiment']['study']['study_identifier'],
                ser['experiment']['study']['published'],

                ser['chemical']['id'],
                ser['chemical']['name'],
                ser['chemical']['cas'],
                ser['chemical']['purity'],

                ser['experiment']['id'],
                ser['experiment']['cell_type']['id'],
                ser['experiment']['cell_type']['species'],
                ser['experiment']['cell_type']['strain'],
                ser['experiment']['cell_type']['sex'],
                ser['experiment']['cell_type']['cell_type'],
                ser['experiment']['cell_type']['tissue'],

                ser['experiment']['dose_units']['name'],
                ser['experiment']['metabolic_activation'],
                ser['experiment']['transfection'],

                ser['id'],
                ser['name'],
                '|'.join([d['name'] for d in ser['effects']]),
                ser['assay_type'],
                ser['short_description'],
                ser['response_units'],
                ser['observation_time'],
                ser['observation_time_units'],
                doseRange[0],
                getDose(ser, 'NOEL'),
                getDose(ser, 'LOEL'),
                doseRange[1],
                ser['monotonicity'],
                ser['overall_pattern'],
                ser['trend_test'],
            ]

            # endpoint-group information
            for i, eg in enumerate(ser['groups']):
                row_copy = copy(row)
                row_copy.extend([
                    eg['id'],
                    eg['dose_group_id'],
                    eg['dose'],
                    eg['n'],
                    eg['response'],
                    eg['stdev'],
                    eg['percentControlMean'],
                    eg['percentControlLow'],
                    eg['percentControlHigh'],
                    eg['difference_control_symbol'],
                    eg['significant_control'],
                    eg['cytotoxicity_observed'],
                    eg['precipitation_observed'],
                ])
                rows.append(row_copy)

        return rows
