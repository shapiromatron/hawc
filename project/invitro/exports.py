from utils.helper import FlatFileExporter


class IVEndpointFlatDataPivot(FlatFileExporter):

    def _get_header_row(self):
        header = [
            'Study',
            'Study HAWC ID',
            'Study identifier',
            'Study URL',
            'Study Published',

            'Chemical name',
            'Chemical CAS',
            'Chemical purity',

            'Cell species',
            'Cell sex',
            'Cell type',
            'Cell tissue',

            'Dose units',
            'Metabolic activation',
            'Transfection',
            'Cell line',

            'Endpoint HAWC ID',
            'Endpoint name',
            'Endpoint URL',
            'Endpoint description tags',
            'Assay type',
            'Endpoint description',
            'Endpoint response units',
            'Observation time',
            'Observation time units',
            'NOAEL',
            'LOAEL',
            'Monotonicity',
            'Overall pattern',
            'Trend test result',
            'Minimum dose',
            'Maximum dose'
        ]

        num_doses = self.queryset.model.get_maximum_number_doses(self.queryset)
        header.extend(["Dose {0}".format(i)        for i in xrange(1, num_doses+1)])
        header.extend(["Change Control {0}".format(i) for i in xrange(1, num_doses+1)])
        header.extend(["Significant {0}".format(i) for i in xrange(1, num_doses+1)])

        num_bms = self.queryset.model.get_maximum_number_benchmarks(self.queryset)
        header.extend(["Benchmark Type {0}".format(i)  for i in xrange(1, num_bms+1)])
        header.extend(["Benchmark Value {0}".format(i) for i in xrange(1, num_bms+1)])

        self.num_doses = num_doses
        self.num_bms = num_bms

        return header

    def _get_data_rows(self):
        rows = []

        for obj in self.queryset:
            ser = obj.get_json(json_encode=False)

            # get min and max doses or None
            min_dose = None
            max_dose = None
            doses = [ eg['dose'] for eg in ser['groups'] ]
            diffs = [ eg['difference_control']  for eg in ser['groups'] ]
            sigs  = [ eg['significant_control'] for eg in ser['groups'] ]
            if len(doses)>0:
                min_dose = min(d for d in doses if d>0)
                max_dose = max(doses)

            bm_types = [bm["benchmark"] for bm in ser["benchmarks"]]
            bm_values = [bm["value"] for bm in ser["benchmarks"]]

            row = [
                ser['experiment']['study']['short_citation'],
                ser['experiment']['study']['id'],
                ser['experiment']['study']['study_identifier'],
                ser['experiment']['study']['url'],
                ser['experiment']['study']['published'],

                ser['chemical']['name'],
                ser['chemical']['cas'],
                ser['chemical']['purity'],

                ser['experiment']['cell_type']['species'],
                ser['experiment']['cell_type']['sex'],
                ser['experiment']['cell_type']['cell_type'],
                ser['experiment']['cell_type']['tissue'],

                ser['experiment']['dose_units']['units'],
                ser['experiment']['metabolic_activation'],
                ser['experiment']['transfection'],
                ser['experiment']['cell_line'],

                ser['id'],
                ser['name'],
                'add URL',
                '|'.join([d['name'] for d in ser['effects']]),
                ser['assay_type'],
                ser['short_description'],
                ser['response_units'],
                ser['observation_time'],
                ser['observation_time_units'],
                ser['groups'][ser['NOAEL']]['dose'] if ser['NOAEL'] != -999 else None,
                ser['groups'][ser['LOAEL']]['dose'] if ser['LOAEL'] != -999 else None,
                ser['monotonicity'],
                ser['overall_pattern'],
                ser['trend_test'],
                min_dose,
                max_dose
            ]

            # extend rows to include blank placeholders, and apply
            doses.extend([None] * (self.num_doses-len(doses)))
            diffs.extend([None] * (self.num_doses-len(diffs)))
            sigs.extend([None] * (self.num_doses-len(sigs)))

            bm_types.extend([None] * (self.num_bms-len(bm_types)))
            bm_values.extend([None] * (self.num_bms-len(bm_values)))

            row.extend(doses)
            row.extend(diffs)
            row.extend(sigs)
            row.extend(bm_types)
            row.extend(bm_values)

            rows.append(row)

        return rows


