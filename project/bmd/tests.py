import os
import logging

from json import loads, dumps
from django.conf import settings
from django.utils import unittest

import xlwt
import shutil

from animal.models import Endpoint, EndpointGroup
from animal.tests import build_endpoints_for_permission_testing
from assessment.models import Assessment
from study.models import Study

import bmds.bmd_models as bmd
from bmd.models import BMD_model_run, BMD_session
from bmd.bmds.bmds import BMDS
from bmd.bmds.output_parser import BMD_output_parser


BMDS_TEST_PATH = os.path.join(settings.BMD_ROOT_PATH, 'bmds_test_cases')

class ModelCompilationReport(unittest.TestCase):
    """
    Base unit test suite provided from EPA using the 100 model-runs which
    they use to test dichotomous files. Compare to validate against
    existing model runs using EPA BMDS outputs.

    The goal of this test is to ensure that output files can be regenerated
    using the same sets of model runs using the Windows-compiled standard BMDS
    modeling outputs and Linux compiled models for use with HAWC online.

    Note that an Excel report as well as numerous output files are created;
    no testing is actually performed in this test-script.
    """

    def setUp(self):
        self.default_d_models = [
            {'model_name': 'Weibull',     'override': {}, 'override_text': []},
            {'model_name': 'Probit',      'override': {}, 'override_text': []},
            {'model_name': 'LogProbit',   'override': {}, 'override_text': []},
            {'model_name': 'Multistage',  'override': {}, 'override_text': []},
            {'model_name': 'Gamma',       'override': {}, 'override_text': []},
            {'model_name': 'Logistic',    'override': {}, 'override_text': []},
            {'model_name': 'LogLogistic', 'override': {}, 'override_text': []}
        ]

        self.default_c_models = [
            {'model_name': 'Power',          'override': {}, 'override_text': []},
            {'model_name': 'Hill',           'override': {}, 'override_text': []},
            {'model_name': 'Linear',         'override': {}, 'override_text': []},
            {'model_name': 'Polynomial',     'override': {}, 'override_text': []},
            {'model_name': 'Exponential-M2', 'override': {}, 'override_text': []},
            {'model_name': 'Exponential-M3', 'override': {}, 'override_text': []},
            {'model_name': 'Exponential-M4', 'override': {}, 'override_text': []},
            {'model_name': 'Exponential-M5', 'override': {}, 'override_text': []},
        ]

    def _load_dichotomous(self, fn):
        """
        First column is dose, second is count affected,
        third is count not affected.
        """
        f = open(fn, 'r')
        dataset = {'dose': [], 'incidence': [], 'n': []}
        for l in f:
            y = [float(v) for v in l.split()]
            dataset['dose'].append(y[0])
            dataset['incidence'].append(y[1])
            dataset['n'].append(y[2]+y[1])
        f.close()
        return dataset

    def _load_continuous(self, fn):
        """
        First column is dose, second is incidence,
        third is response, fourth is std. dev.
        """
        f = open(fn, 'r')
        dataset = {'dose': [], 'n': [], 'response': [], 'stdev': []}
        for l in f:
            y = [float(v) for v in l.split()]
            dataset['dose'].append(y[0])
            dataset['n'].append(y[1])
            dataset['response'].append(y[2])
            dataset['stdev'].append(y[3])
        f.close()
        return dataset

    def _create_xls_wb(self):
        # create excel file
        wb = xlwt.Workbook()
        ws = wb.add_sheet("outputs")
        header_fmt = xlwt.easyxf('font: colour black, bold True;')

        # freeze panes on header
        ws.set_panes_frozen(True)
        ws.horz_split_pos = 1

        # write header
        for col, val in enumerate(['ID', 'Filename', 'Model', 'BMD', 'BMDL', "AIC"]):
            ws.write(0, col, val, style=header_fmt)

        return (wb, ws)

    def _get_dichotomous_endpoint_d(self, dataset):
        """
        Hack of the standard way to return an endpoint dictionary for the 100
        test-case runs. This is because creating an endpoint requires a large
        number of various django models that must be created for one endpoint,
        so we simplify this process to what is required.
        """
        drs = []
        for i,v in enumerate(dataset['dose']):
            drs.append({
                'dose': dataset['dose'][i],
                'incidence': dataset['incidence'][i],
                'n': dataset['n'][i]
                })

        return {'numDG': len(drs), 'dr': drs}

    def _get_continuous_endpoint_d(self, dataset):
        """
        Hack of the standard way to return an endpoint dictionary for the 100
        test-case runs. This is because creating an endpoint requires a large
        number of various django models that must be created for one endpoint,
        so we simplify this process to what is required.
        """
        drs = []
        for i,v in enumerate(dataset['dose']):
            drs.append({
                'dose': dataset['dose'][i],
                'n': dataset['n'][i],
                'response': dataset['response'][i],
                'stdev': dataset['stdev'][i]
                })

        inc = dataset['response'][i]>dataset['response'][0]

        return {'numDG': len(drs), 'dr': drs, 'dataset_increasing': inc}

    def _print_individual_run(self, ws, results, file_identifier, model_name, row, output_path, d_file):
        d_fn = '{0}-{1}.(d)'.format(file_identifier, model_name)
        with open(os.path.join(output_path, d_fn), 'w') as output:
            output.write(d_file)

        out_fn = '{0}-{1}.out'.format(file_identifier, model_name)
        with open(os.path.join(output_path, out_fn), 'w') as output:
            output.write(results['output_text'])

        ws.write(row, 0, row)
        ws.write(row, 1, file_identifier)
        ws.write(row, 2, model_name)
        ws.write(row, 3, results['outputs']['BMD'])
        ws.write(row, 4, results['outputs']['BMDL'])
        ws.write(row, 5, results['outputs']['AIC'])

    def _run_dichotomous(self, version):
        """
        One change made to input files: 038.dat, dropped highest dose. Confirmed
        that this causes the standard BMDS models to hard-hang and therefore,
        removed the high dose from this case which fixed modeling issue.
        """
        output_folder =  version.replace(".", "") + "_outputs"
        input_path = os.path.join(BMDS_TEST_PATH, 'dichotomous', 'inputs')
        output_path = os.path.join(BMDS_TEST_PATH, 'dichotomous', output_folder)
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        os.makedirs(output_path)

        wb, ws = self._create_xls_wb()
        row=0

        # begin model runs
        bmds = BMDS.versions[version]()
        files = sorted(os.listdir(input_path))
        for f in files:
            fn = os.path.join(input_path, f)
            dataset = self._load_dichotomous(fn)
            endpoint_d = self._get_dichotomous_endpoint_d(dataset)
            for setting in self.default_d_models:
                row+=1
                #change the poly degree for the multistage model
                if setting['model_name'] == 'Multistage':
                    setting['override']['degree_poly'] = len(dataset)-1

                # get default bmds settings
                logging.debug('Running {0}:{1}'.format(f, setting['model_name']))
                run_instance = bmds.models['D'][setting['model_name']]()
                d_file = run_instance.dfile_print(endpoint_d)

                model = BMD_model_run(model_name=run_instance.model_name)
                results = model.execute_bmds(bmds,
                                             run_instance,
                                             d_file,
                                             create_image=False)
                file_identifier = f[:(len(f)-4)]
                model_name = run_instance.model_name
                self._print_individual_run(ws, results, file_identifier,
                                           model_name, row, output_path,
                                           d_file)

        # save excel file
        wb.save(os.path.join(output_path, 'outputs.xls'))

    def _run_continuous(self, version):
        """
        Changed one session file:
            - 012.txt resp & stdev changed from 0.0 to 0.1. Confirmed that this
              session file causes the BMDS GUI to crash as well.
        """
        output_folder =  version.replace(".", "") + "_outputs"
        input_path = os.path.join(BMDS_TEST_PATH, 'continuous', 'inputs')
        output_path = os.path.join(BMDS_TEST_PATH, 'continuous', output_folder)
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        os.makedirs(output_path)

        wb, ws = self._create_xls_wb()
        row=0

        # begin model runs
        bmds = BMDS.versions[version]()
        files = sorted(os.listdir(input_path))
        for f in files:
            fn = os.path.join(input_path, f)
            dataset = self._load_continuous(fn)
            endpoint_d = self._get_continuous_endpoint_d(dataset)
            for setting in self.default_c_models:
                # get default bmds settings
                run_instance = bmds.models['C'][setting['model_name']]()
                runnable = endpoint_d['numDG'] >= run_instance.minimum_DG
                if runnable:
                    row+=1
                    logging.debug('Running {0}:{1}'.format(f, setting['model_name']))

                    #change the poly degree for the multistage model
                    if setting['model_name'] == 'Polynomial':
                        setting['override']['degree_poly'] = endpoint_d['numDG']-1
                        if endpoint_d['dataset_increasing']:
                            setting['override']['restrict_polynomial'] = 1
                        else:
                            setting['override']['restrict_polynomial'] = -1

                    d_file = run_instance.dfile_print(endpoint_d)
                    model = BMD_model_run(model_name=run_instance.model_name)
                    results = model.execute_bmds(bmds,
                                                 run_instance,
                                                 d_file,
                                                 create_image=False)
                    file_identifier = f[:(len(f)-4)]
                    model_name = setting['model_name']
                    self._print_individual_run(ws, results, file_identifier,
                                               model_name, row, output_path,
                                               d_file)

        # save excel file
        wb.save(os.path.join(output_path, 'outputs.xls'))

    def _clear_path(self, path):
        for f in os.listdir(path):
            os.remove(f)

    def test_dichotomous_230(self):
        self._run_dichotomous('2.30')

    def test_dichotomous_231(self):
        self._run_dichotomous('2.31')

    def test_dichotomous_240(self):
        self._run_dichotomous('2.40')

    def test_continuous_230(self):
        self._run_continuous('2.30')

    def test_continuous_231(self):
        self._run_continuous('2.31')

    def test_continuous_240(self):
        self._run_continuous('2.40')


class DFileComparisons(unittest.TestCase):
    """
    Ensure that "default" d-file settings using BMDS GUI are equivalent to those
    generated using HAWC.
    """
    def _clean_d_file(self, txt):
        """
        Remove the filename path line since that may not be identical.
        """
        txts = txt.split('\n')
        txts.pop(3)
        txts.pop(2)
        return '\n'.join(txts)

    def test_dichotomous(self):
        input_path = os.path.join(BMDS_TEST_PATH, 'dichotomous', 'inputs')
        output_path = os.path.join(BMDS_TEST_PATH, 'dichotomous', '230_outputs')
        bmds = BMDS.versions['2.40']()
        for (path, dirs, files) in os.walk(input_path):
            for f in files:
                fn = os.path.join(path, f)
                dataset = self.load_from_file(fn)
                endpoint_d = self.get_endpoint_d(dataset)

                #change the poly degree for the multistage model
                for setting in self.default_models:
                    if setting['model_name'] == 'Multistage':
                        setting['override']['degree_poly'] = len(dataset)-1

                    # get default bmds settings
                    logging.debug('Running ' + fn)
                    run_instance = bmds.models['D'][setting['model_name']]()
                    d_file = self._clean_d_file(run_instance.dfile_print(endpoint_d))

                    # load gold-standard file
                    out_file = f.replace('.dat', '-%s.(d)' % (setting['model_name']))
                    fn = os.path.join(output_path, out_file)
                    gold_standard_d_file = self._clean_d_file(open(fn, 'r').read())

                    # confirm they're the same
                    self.assertEqual(d_file, gold_standard_d_file)


class BMDRunTests(unittest.TestCase):
    """
    Unit-tests for ensuring that some inputs can be edited and modified when
    modeling basic continuous and dichotomous datasets.
    """

    def setUp(self):
        self.v = BMDS.versions['2.30']()
        self.dummy_dataset = {
            "numDG": 5,
            'dr':
            [
                {'dose': 0,   'incidence': 0, 'n': 20},
                {'dose': 50,  'incidence': 0, 'n': 20},
                {'dose': 150, 'incidence': 3, 'n': 20},
                {'dose': 250, 'incidence': 6, 'n': 20},
                {'dose': 350, 'incidence': 6, 'n': 20}
            ]
        }
        self.bmr_d = {'type': 'Extra', 'value': 0.1, 'confidence_level': 0.95}
        self.bmr_c = {'type': 'Std. Dev.', 'value': 1.0, 'confidence_level': 0.95}
        self.dataset_dichotomous = {
            'LOAEL': -999,
            'NOAEL': -999,
            'data_type': u'D',
            'dose_units': u'mg/kg/day',
            'dr': [{'dose': 0.0,
                    'dose_group_id': 0,
                    'incidence': 1,
                    'n': 20,
                    'response': None,
                    'stdev': None},
                   {'dose': 50.0,
                    'dose_group_id': 1,
                    'incidence': 3,
                    'n': 20,
                    'response': None,
                    'stdev': None},
                   {'dose': 150.0,
                    'dose_group_id': 2,
                    'incidence': 5,
                    'n': 20,
                    'response': None,
                    'stdev': None},
                   {'dose': 350.0,
                    'dose_group_id': 3,
                    'incidence': 7,
                    'n': 20,
                    'response': None,
                    'stdev': None}],
            'name': u'foo2',
            'numDG': 4,
            'response_units': u'mg/hr',
            'session': None,
            'template': None
        }
        self.dataset_continuous = {
            'LOAEL': -999,
            'NOAEL': -999,
            'data_type': u'D',
            'dose_units': u'mg/kg/day',
            'dr': [{'dose': 0.0,
                    'dose_group_id': 0,
                    'incidence': None,
                    'n': 20,
                    'response': 11.,
                    'stdev': 2.4},
                   {'dose': 50.0,
                    'dose_group_id': 1,
                    'incidence': None,
                    'n': 20,
                    'response': 16.,
                    'stdev': 3.4},
                   {'dose': 150.0,
                    'dose_group_id': 2,
                    'incidence': None,
                    'n': 20,
                    'response': 19.,
                    'stdev': 5.7},
                   {'dose': 350.0,
                    'dose_group_id': 3,
                    'incidence': None,
                    'n': 20,
                    'response': 21.,
                    'stdev': 6.7},
                   {'dose': 450.0,
                    'dose_group_id': 4,
                    'incidence': None,
                    'n': 20,
                    'response': 32.,
                    'stdev': 9.1}],
            'name': u'foo2',
            'numDG': 5,
            'response_units': u'mg/hr',
            'session': None,
            'template': None
        }

    def test_override(self):
        """ Check to make sure model-specific parameters are overriden """
        model = bmd.Logistic_213()
        override = {'max_iterations': 200}
        model.update_model(override, ['max iterations = 200'], self.bmr_d)
        self.assertTrue(model.override_txt[0] == 'max iterations = 200')
        self.assertTrue(model.values['max_iterations'][0] == 200)

    def test_check_no_dose_drop(self):
        """ Check to make sure no doses are dropped originally """
        model = bmd.Logistic_213()
        model.values['dose_drop'] = (0, False)
        v = model._dfile_print_dichotomous_dataset(self.dummy_dataset)
        self.assertTrue(v == """Dose Incidence NEGATIVE_RESPONSE\n0.000000 0 20\n50.000000 0 20\n150.000000 3 17\n250.000000 6 14\n350.000000 6 14\n""")

    def test_check_one_dose_drop(self):
        """ Check to make sure a dose is dropped properly """
        model = bmd.Logistic_213()
        override = {'dose_drop': 1}
        model.update_model(override, ['doses dropped = 1'], self.bmr_d)
        v = model._dfile_print_dichotomous_dataset(self.dummy_dataset)
        self.assertTrue(v == """Dose Incidence NEGATIVE_RESPONSE\n0.000000 0 20\n50.000000 0 20\n150.000000 3 17\n250.000000 6 14\n""")

    def test_bmd_dfile(self):
        """ Check to make sure a dfile can succesfully be printed """
        m_run = self.v.models['D']['Logistic']()
        dfile = m_run.dfile_print(self.dataset_dichotomous)
        self.assertTrue(dfile == 'Logistic\nBMDS_Model_Run\n/temp/bmd/datafile.dax\n/temp/bmd/output.out\n4\n250 1e-08 1e-08 0 0 0 1 0 0\n0.1 0 0.95\n-9999 -9999 -9999\n0\n-9999 -9999 -9999\nDose Incidence NEGATIVE_RESPONSE\n0.000000 1 19\n50.000000 3 17\n150.000000 5 15\n350.000000 7 13\n')

    def import_bmds_output_file(self, fn):
        """
        Read the full output file from BMDS, but drop the first ten header
        lines because they'll timestamp information which will make our diff
        comparison wrong.
        """
        x = open(fn).read()
        return x.splitlines()[10:]

    def test_run_Dichotomous_231(self):
        """
        Test suite for standard Dichotomous 2.3.1. models. This test contains
        basic models, with very minimal modifications. It also assumes the
        standard 10% BMR check. Note that in a few multistage cases, the
        degree_poly value is overridden from the default.
        """
        session = BMD_session(BMDS_version='2.31', bmrs=self.bmr_d)
        run_suite = (
            {
                'type': 'Logistic',
                'fn': '1-dichotomous-tc-Logistic-10%.out'
            },
            {
                'type': 'LogLogistic',
                'fn': '1-dichotomous-tc-LogLogistic-10%.out'
            },
            {
                'type': 'Weibull',
                'fn': '1-dichotomous-tc-Weibull-10%.out'
            },
            {
                'type': 'Probit',
                'fn': '1-dichotomous-tc-Probit-10%.out'
            },
            {
                'type': 'LogProbit',
                'fn': '1-dichotomous-tc-LogProbit-10%.out'
            },
            {
                'type': 'Gamma',
                'fn': '1-dichotomous-tc-Gamma-10%.out'
            },
            {
                'type': 'Multistage',
                'fn': '1-dichotomous-tc-Multi1-10%.out',
                'override': {'degree_poly': 1},
                'override_text': ['Degree of Polynomial = 1']
            },
            {
                'type': 'Multistage',
                'fn': '1-dichotomous-tc-Multi2-10%.out',
                'override': {'degree_poly': 2},   # todo: these lines shouldn't be required, think parent class needs to update child class
                'override_text': ['Degree of Polynomial = 2']
            },
            {
                'type': 'Multistage',
                'fn': '1-dichotomous-tc-Multi3-10%.out',
                'override': {'degree_poly': 3},
                'override_text': ['Degree of Polynomial = 3']
            },
        )
        for run in run_suite:
            logging.debug('Testing ' + run['fn'])
            m_run = self.v.models['D'][run['type']]()
            if 'override' in run:
                m_run.update_model(run['override'], run['override_text'], self.bmr_d)
            m = BMD_model_run(model_name=run['type'],
                              BMD_session=session,
                              option_override={},
                              option_override_text=[""])
            m.run_model(self.v, m_run, self.dataset_dichotomous)
            output_text = m.output_text.splitlines()[10:]
            fn = os.path.join(BMDS_231_TESTPATH, run['fn'])
            gold_standard = self.import_bmds_output_file(fn)
            # f = file(os.path.join(BMDS_231_TESTPATH, 'test_output.txt'), 'w')
            # f.write('\n'.join(output_text))
            # f.close()
            # f = file(os.path.join(BMDS_231_TESTPATH, 'gold_standard.txt'), 'w')
            # f.write('\n'.join(gold_standard))
            # f.close()
            self.assertTrue(output_text == gold_standard)

    def test_run_Continuous_231(self):
        """
        Test suite for standard Continuous 2.3.1. models. This test contains
        basic models, with very minimal modifications. It also assumes the
        standard 1 SD BMR. Note that in the polynomial case, the
        degree_poly value is overridden from the default.
        """
        session = BMD_session(BMDS_version='2.31', bmrs=self.bmr_c)
        run_suite = (
            {
                'type': 'Linear',
                'fn': '2-continuous-tc-LinearCV-1SD.out'
            },
            {
                'type': 'Polynomial',
                'fn': '2-continuous-tc-Poly4CV-1SD.out',
                'override': {
                    'degree_poly': 4,
                    'restrict_polynomial': 1
                },
                'override_text': ['Degree of Polynomial = 4']
            },
            {
                'type': 'Power',
                'fn': '2-continuous-tc-PowerCV-1SD.out'
            },
            {
                'type': 'Hill',
                'fn': '2-continuous-tc-HillCV-1SD.out'
            },
            {
                'type': 'Exponential-M2',
                'fn': '2-continuous-tc-M2M2ExpCV-1SD.out'
            },
            {
                'type': 'Exponential-M3',
                'fn': '2-continuous-tc-M3M3ExpCV-1SD.out'
            },
            {
                'type': 'Exponential-M4',
                'fn': '2-continuous-tc-M4M4ExpCV-1SD.out'
            },
            {
                'type': 'Exponential-M5',
                'fn': '2-continuous-tc-M5M5ExpCV-1SD.out'
            },
        )
        for run in run_suite:
            logging.debug('Testing ' + run['fn'])
            m_run = self.v.models['C'][run['type']]()
            if 'override' in run:
                m_run.update_model(run['override'], run['override_text'], self.bmr_c)
            m = BMD_model_run(model_name=run['type'],
                              BMD_session=session,
                              option_override={},
                              option_override_text=[""])
            m.run_model(self.v, m_run, self.dataset_continuous)
            output_text = m.output_text.splitlines()[10:]
            fn = os.path.join(BMDS_231_TESTPATH, run['fn'])
            gold_standard = self.import_bmds_output_file(fn)
            # f = file(os.path.join(BMDS_231_TESTPATH, 'test_output.txt'), 'w')
            # f.write('\n'.join(output_text))
            # f.close()
            # f = file(os.path.join(BMDS_231_TESTPATH, 'gold_standard.txt'), 'w')
            # f.write('\n'.join(gold_standard))
            # f.close()
            self.assertTrue(output_text == gold_standard)

    def test_force_kill(self):
        """
        Ensure that BMDS models are killed by the subprocess module as expected
        for a dataset known to cause issues. This dataset is confirmed to
        cause an infinite loop, and thus should be killed.
        """

        dataset = {'dose': [0., 75., 250.],
                   'n': [11, 11, 11],
                   'response': [0., 0.3, 1.8],
                   'stdev': [0., 0.544, 2.01]}
        endpoint = self.save_endpoint(dataset)

        settings = {
            'options': [{'model_name': 'Exponential-M2',
                         'override': {},
                         'override_text': []}],
            'bmrs': [{'type': 'Std. Dev.',
                      'value': 1.0,
                      'confidence_level': 0.95}],
        }

        session = BMD_session(endpoint=endpoint,
                              BMDS_version='2.40',
                              bmrs=dumps(self.default_bmrs))
        session.save()
        session.run_session(endpoint, settings)

        models = BMD_model_run.objects.filter(BMD_session=session)
        for model in models:
            self.assertTrue(model.runtime_error)
