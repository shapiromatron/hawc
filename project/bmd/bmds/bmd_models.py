from json import dumps

BMR_CROSSWALK = {
    'D': {
        'Extra': 0,
        'Added': 1
    },
    'DC': {
        'Extra': 0
    },
    'C': {
        'Abs. Dev.': 0,
        'Std. Dev.': 1,
        'Rel. Dev.': 2,
        'Point': 3,
        'Extra': 4
    }
}


class BMDModel(object):
    """
    Has the following required static-class methods:

        - model_name = ''      # string model name
        - dtype = ''           # data type - 'D','C', etc.
        - exe = ''             # BMD executable (without extension)
        - exe_plot             # wgnuplot input-file executable (without extension)
        - version = 0          # version number
        - date = ''            # version date
        - defaults = {}        # default options setup
        - possible_bmr = ()    # possible BMRs which can be used w/ model

    And at-least these instance methods:

        - self.override = {}        # overridden values from default
        - self.override_txt = ['']  # text string(s) for overridden values
        - self.values = {}          # full values for object

    Default key fields:
      - c = category
      - t = type
      - f = fixed
      - n = name

    """

    def build_defaults(self, json=False):
        """
        Build default options dictionary for the BMD model, returning only
        values which can be changed the by the user.
        """
        opt = {}
        for k, v in self.defaults.iteritems():
            if v['f'] == 0:    # if not fixed
                opt[k] = v
        return dumps(opt) if json else opt

    def valid_bmr(self, bmr):
        #given a model instance, check if a BMR is valid for this model-type
        return bmr['type'] in self.possible_bmr

    def update_model(self, override, override_txt, bmr):
        """
        Update the override dictionary and override text dictionary,
        save new values. Also update the bmr option selected.
        """
        self.override = override
        self.override_txt = override_txt
        for k, v in self.override.iteritems():
            if str(v).find('|') == -1:
                self.values[k] = (v, False)
            else:
                self.values[k] = (v.split('|'))

        self.values['bmr_type'] = (BMR_CROSSWALK[self.dtype][bmr['type']], False)
        self.values['bmr'] = (bmr['value'], False)
        self.values['confidence_level'] = (bmr['confidence_level'], False)

    def _get_option_value(self, key):
        """
        Get option value(s), or use default value if no override value.
        Two output values for 'p' type values (parameters), else one. Returns
        a tuple of two values.
        """
        if key in self.override:
            val = self.override[key]
        else:
            val = self.defaults[key]['d']
        if self.defaults[key]['t'] == 'p':  # parameter (two values)
            return val.split('|')
        else:
            return val, False

    def _dfile_print_header(self):
        return [self.model_name, 'BMDS_Model_Run',
                '/temp/bmd/datafile.dax', '/temp/bmd/output.out']

    def _dfile_print_parameters(self, order):
        #Print parameters in the specified order. Expects a tuple of parameter
        # names, in the proper order.
        if ((self.dtype == 'C') and (self.values['constant_variance'][0] == 1)):
            self.values['rho'] = ('s', 0)  # for specified to equal 0
        specs = []
        inits = []
        init = '0'  # 1 if initialized, 0 otherwise
        for i in order:
            t, v = self.values[i]
            #now save values
            if t == 'd':
                specs.append(-9999)
                inits.append(-9999)
            elif t == 's':
                specs.append(v)
                inits.append(-9999)
            elif t == 'i':
                init = '1'
                specs.append(-9999)
                inits.append(v)
        return '\n'.join([' '.join([str(i) for i in specs]),
                          init, ' '.join([str(i) for i in inits])])

    def _dfile_print_dichotomous_dataset(self, dataset):
        # add dose-response dataset, dropping doses as specified
        dropped = self.values['dose_drop'][0]
        txt = 'Dose Incidence NEGATIVE_RESPONSE\n'
        for i, v in enumerate(dataset['dr']):
            if i < len(dataset['dr']) - dropped:
                txt += '%f %d %d\n' % (v['dose'],
                                       v['incidence'],
                                       v['n'] - v['incidence'])
        return txt

    def _dfile_print_continuous_dataset(self, dataset):
        dropped = self.values['dose_drop'][0]
        txt = 'Dose NumAnimals Response Stdev\n'
        for i, v in enumerate(dataset['dr']):
            if i < len(dataset['dr']) - dropped:
                txt += '%f %f %f %f\n' % (v['dose'],
                                          v['n'],
                                          v['response'],
                                          v['stdev'])
        return txt

    def _dfile_print_options(self, order):
        #helper function; given tuple order of parameters in the 'value'
        # dictionary, return a space-separated list
        r = []
        for f in order:
            r.append(self.values[f][0])
        return ' '.join([str(i) for i in r])

    def __init__(self):
        #save default values originally
        self.values = {}
        self.override = {}
        self.override_txt = ['']
        for k, v in self.defaults.iteritems():
            self.values[k] = self._get_option_value(k)


#Continuous models
class Polynomial_216(BMDModel):

    def dfile_print(self, dataset):
        """Custom file for printing dfile, using helper functions for BMD
        parent class."""
        txt = self._dfile_print_header()
        degpoly = int(self.values['degree_poly'][0])
        txt.append(str(degpoly))
        txt.append('1 ' + str(dataset['numDG'] - self.values['dose_drop'][0]) + ' 0')
        p = ('max_iterations', 'relative_fn_conv', 'parameter_conv',
             'bmdl_curve_calculation', 'restrict_polynomial',
             'bmd_calculation', 'append_or_overwrite', 'smooth_option')
        txt.append(self._dfile_print_options(p))
        p = ('bmr_type', 'bmr',  'constant_variance', 'confidence_level')
        txt.append(self._dfile_print_options(p))
        p = ['alpha', 'rho', 'beta_0']
        for i in xrange(1, degpoly + 1):
            p.append('beta_' + str(i))
        txt.append(self._dfile_print_parameters(p))
        txt.append(self._dfile_print_continuous_dataset(dataset))
        return '\n'.join(txt)

    #todo: add check that degree poly must be <=8
    minimum_DG = 2
    model_name = 'Polynomial'
    dtype = 'C'
    exe = 'poly'
    exe_plot = '00poly'
    js_formula = "{beta_0} + ({beta_1}*x) + ({beta_2}*Math.pow(x,2)) + ({beta_3}*Math.pow(x,3)) + ({beta_4}*Math.pow(x,4)) + ({beta_5}*Math.pow(x,5)) + ({beta_6}*Math.pow(x,6)) + ({beta_7}*Math.pow(x,7)) + ({beta_8}*Math.pow(x,8))"
    js_parameters = ['beta_0', 'beta_1', 'beta_2', 'beta_3', 'beta_4', 'beta_5', 'beta_6', 'beta_7', 'beta_8']
    version = 2.16
    date = '05/26/2010'
    defaults = {
        'bmdl_curve_calculation':   {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'append_or_overwrite':      {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'smooth_option':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'max_iterations':           {'c': 'op', 't': 'i', 'f': 0, 'd': 250, 'n': 'Iteration'},
        'relative_fn_conv':         {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Relative Function'},
        'parameter_conv':           {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Parameter'},
        'alpha':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Alpha'},
        'rho':                      {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Rho'},
        'beta_0':                   {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta0'},
        'beta_1':                   {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta1'},
        'beta_2':                   {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta2'},
        'beta_3':                   {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta3'},
        'beta_4':                   {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta4'},
        'beta_5':                   {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta5'},
        'beta_7':                   {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta7'},
        'beta_6':                   {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta6'},
        'beta_8':                   {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta8'},
        'restrict_polynomial':      {'c': 'ot', 't': 'rp', 'f': 0, 'd': 0, 'n': 'Restrict Polynomial'},
        'degree_poly':              {'c': 'ot', 't': 'i', 'f': 0, 'd': 2, 'n': 'Degree of Polynomial'},
        'bmd_calculation':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'BMD Calculation'},
        'bmdl_curve_calc':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 0, 'n': 'BMDL Curve Calculation'},
        'dose_drop':                {'c': 'ot', 't': 'dd', 'f': 0, 'd': 0, 'n': 'Doses to drop'},
        'bmr':                      {'c': 'b',  't': 'd', 'f': 1, 'd': 1.0},
        'bmr_type':                 {'c': 'b',  't': 'i', 'f': 1, 'd': 1},
        'confidence_level':         {'c': 'b',  't': 'd', 'f': 1, 'd': 0.95},
        'constant_variance':        {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'Constant Variance'}}
    possible_bmr = ('Abs. Dev.', 'Std. Dev.', 'Rel. Dev.', 'Point', 'Extra')


class Polynomial_217(Polynomial_216):
    version = 2.17
    date = '01/28/2013'
    defaults = Polynomial_216.defaults.copy()
    defaults['max_iterations']['d'] = 500


class Linear_216(BMDModel):
    """ Overrides of Polynomial for Linear model. """

    def dfile_print(self, dataset):
        """Custom file for printing dfile, using helper functions for BMD
        parent class."""
        txt = self._dfile_print_header()
        txt.append('1')
        txt.append('1 ' + str(dataset['numDG'] - self.values['dose_drop'][0]) + ' 0')
        p = ('max_iterations', 'relative_fn_conv', 'parameter_conv',
             'bmdl_curve_calculation', 'restrict_polynomial',
             'bmd_calculation', 'append_or_overwrite', 'smooth_option')
        txt.append(self._dfile_print_options(p))
        p = ('bmr_type', 'bmr',  'constant_variance', 'confidence_level')
        txt.append(self._dfile_print_options(p))
        p = ['alpha', 'rho', 'beta_0', 'beta_1']
        txt.append(self._dfile_print_parameters(p))
        txt.append(self._dfile_print_continuous_dataset(dataset))
        return '\n'.join(txt)

    #todo: add check that degree poly must be <=8
    minimum_DG = 2
    model_name = 'Linear'
    dtype = 'C'
    exe = 'poly'
    exe_plot = '00poly'
    js_formula = "{beta_0} + ({beta_1}*x)"
    js_parameters = ['beta_0', 'beta_1']
    version = 2.16
    date = '05/26/2010'
    defaults = {
        'bmdl_curve_calculation':   {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'append_or_overwrite':      {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'smooth_option':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'max_iterations':           {'c': 'op', 't': 'i', 'f': 0, 'd': 250, 'n': 'Iteration'},
        'relative_fn_conv':         {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Relative Function'},
        'parameter_conv':           {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Parameter'},
        'alpha':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Alpha'},
        'rho':                      {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Rho'},
        'beta_0':                   {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta0'},
        'beta_1':                   {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta1'},
        'restrict_polynomial':      {'c': 'ot', 't': 'rp', 'f': 0, 'd': 0, 'n': 'Restrict Polynomial'},
        'degree_poly':              {'c': 'ot', 't': 'i', 'f': 1, 'd': 1},
        'bmd_calculation':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'BMD Calculation'},
        'bmdl_curve_calc':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 0, 'n': 'BMDL Curve Calculation'},
        'dose_drop':                {'c': 'ot', 't': 'dd', 'f': 0, 'd': 0, 'n': 'Doses to drop'},
        'bmr':                      {'c': 'b',  't': 'd', 'f': 1, 'd': 1.0},
        'bmr_type':                 {'c': 'b',  't': 'i', 'f': 1, 'd': 1},
        'confidence_level':         {'c': 'b',  't': 'd', 'f': 1, 'd': 0.95},
        'constant_variance':        {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'Constant Variance'}}
    possible_bmr = ('Abs. Dev.', 'Std. Dev.', 'Rel. Dev.', 'Point', 'Extra')


class Linear_217(Linear_216):
    version = 2.17
    date = '01/28/2013'
    defaults = Linear_216.defaults.copy()
    defaults['max_iterations']['d'] = 500


class Exponential_M2_17(BMDModel):

    def dfile_print(self, dataset):
        """
        Custom function for printing exponential dfiles.
        """
        txt = self._dfile_print_header()
        txt.append('1 ' + str(dataset['numDG'] - self.values['dose_drop'][0]) + self.exp_run_settings)
        p = ('max_iterations', 'relative_fn_conv', 'parameter_conv',
             'bmdl_curve_calculation', 'bmd_calculation',
             'append_or_overwrite', 'smooth_option')
        txt.append(self._dfile_print_options(p))
        p = ('bmr_type', 'bmr', 'constant_variance', 'confidence_level')
        txt.append(self._dfile_print_options(p))
        p = ('alpha', 'rho', 'a', 'b', 'c', 'd')
        v = self._dfile_print_parameters(p)
        txt.append('\n'.join([v for i in xrange(4)]))
        txt.append(self._dfile_print_continuous_dataset(dataset))
        return '\n'.join(txt)

    minimum_DG = 2
    pretty_name = 'Exponential-M2'
    model_name = 'Exponential'
    dtype = 'C'
    exe = 'exponential'
    exe_plot = 'Expo_CPlot'
    js_formula = "{a} * Math.exp({sign}*{b}*x)"
    exp_run_settings = ' 0 1000 11 0 1'
    js_parameters = ['a', 'b', 'sign']
    version = 1.7
    date = '12/10/2009'
    defaults = {
        'bmdl_curve_calculation':   {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'append_or_overwrite':      {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'smooth_option':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'max_iterations':           {'c': 'op', 't': 'i', 'f': 0, 'd': 250, 'n': 'Iteration'},
        'relative_fn_conv':         {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Relative Function'},
        'parameter_conv':           {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Parameter'},
        'alpha':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Alpha'},
        'rho':                      {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Rho'},
        'a':                        {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'a'},
        'b':                        {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'b'},
        'c':                        {'c': 'p',  't': 'p', 'f': 1, 'd': 'd|', 'n': 'c'},
        'd':                        {'c': 'p',  't': 'p', 'f': 1, 'd': 'd|', 'n': 'd'},
        'bmd_calculation':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'BMD Calculation'},
        'bmdl_curve_calc':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 0, 'n': 'BMDL Curve Calculation'},
        'dose_drop':                {'c': 'ot', 't': 'dd', 'f': 0, 'd': 0, 'n': 'Doses to drop'},
        'bmr':                      {'c': 'b',  't': 'd', 'f': 1, 'd': 1.0},
        'bmr_type':                 {'c': 'b',  't': 'i', 'f': 1, 'd': 1},
        'confidence_level':         {'c': 'b',  't': 'd', 'f': 1, 'd': 0.95},
        'constant_variance':        {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'Constant Variance'}}
    possible_bmr = ('Abs. Dev.', 'Std. Dev.', 'Rel. Dev.', 'Point', 'Extra')
    output_prefix = 'M2'


class Exponential_M2_19(Exponential_M2_17):
    version = 1.9
    date = '01/29/2013'
    defaults = Exponential_M2_17.defaults.copy()
    defaults['max_iterations']['d'] = 500


class Exponential_M3_17(BMDModel):

    def dfile_print(self, dataset):
        """
        Custom function for printing exponential dfiles.
        """
        txt = self._dfile_print_header()
        txt.append('1 ' + str(dataset['numDG'] - self.values['dose_drop'][0]) + self.exp_run_settings)
        p = ('max_iterations', 'relative_fn_conv', 'parameter_conv',
             'bmdl_curve_calculation', 'bmd_calculation',
             'append_or_overwrite', 'smooth_option')
        txt.append(self._dfile_print_options(p))
        p = ('bmr_type', 'bmr', 'constant_variance', 'confidence_level')
        txt.append(self._dfile_print_options(p))
        p = ('alpha', 'rho', 'a', 'b', 'c', 'd')
        v = self._dfile_print_parameters(p)
        txt.append('\n'.join([v for i in xrange(4)]))
        txt.append(self._dfile_print_continuous_dataset(dataset))
        return '\n'.join(txt)

    minimum_DG = 3
    pretty_name = 'Exponential-M3'
    model_name = 'Exponential'
    dtype = 'C'
    exe = 'exponential'
    exe_plot = 'Expo_CPlot'
    js_formula = "{a} * Math.exp({sign}*Math.pow({b}*x,{d}))"
    exp_run_settings = ' 0 0100 22 0 1'
    js_parameters = ['a', 'b', 'd', 'sign']
    version = 1.7
    date = '12/10/2009'
    defaults = {
        'bmdl_curve_calculation':   {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'append_or_overwrite':      {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'smooth_option':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'max_iterations':           {'c': 'op', 't': 'i', 'f': 0, 'd': 250, 'n': 'Iteration'},
        'relative_fn_conv':         {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Relative Function'},
        'parameter_conv':           {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Parameter'},
        'alpha':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Alpha'},
        'rho':                      {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Rho'},
        'a':                        {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'a'},
        'b':                        {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'b'},
        'c':                        {'c': 'p',  't': 'p', 'f': 1, 'd': 'd|', 'n': 'c'},
        'd':                        {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'd'},
        'bmd_calculation':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'BMD Calculation'},
        'bmdl_curve_calc':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 0, 'n': 'BMDL Curve Calculation'},
        'dose_drop':                {'c': 'ot', 't': 'dd', 'f': 0, 'd': 0, 'n': 'Doses to drop'},
        'bmr':                      {'c': 'b',  't': 'd', 'f': 1, 'd': 1.0},
        'bmr_type':                 {'c': 'b',  't': 'i', 'f': 1, 'd': 1},
        'confidence_level':         {'c': 'b',  't': 'd', 'f': 1, 'd': 0.95},
        'constant_variance':        {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'Constant Variance'}}
    possible_bmr = ('Abs. Dev.', 'Std. Dev.', 'Rel. Dev.', 'Point', 'Extra')
    output_prefix = 'M3'


class Exponential_M3_19(Exponential_M3_17):
    version = 1.9
    ddate = '01/29/2013'
    defaults = Exponential_M3_17.defaults.copy()
    defaults['max_iterations']['d'] = 500


class Exponential_M4_17(BMDModel):

    def dfile_print(self, dataset):
        """
        Custom function for printing exponential dfiles.
        """
        txt = self._dfile_print_header()
        txt.append('1 ' + str(dataset['numDG'] - self.values['dose_drop'][0]) + self.exp_run_settings)
        p = ('max_iterations', 'relative_fn_conv', 'parameter_conv',
             'bmdl_curve_calculation', 'bmd_calculation',
             'append_or_overwrite', 'smooth_option')
        txt.append(self._dfile_print_options(p))
        p = ('bmr_type', 'bmr', 'constant_variance', 'confidence_level')
        txt.append(self._dfile_print_options(p))
        p = ('alpha', 'rho', 'a', 'b', 'c', 'd')
        v = self._dfile_print_parameters(p)
        txt.append('\n'.join([v for i in xrange(4)]))
        txt.append(self._dfile_print_continuous_dataset(dataset))
        return '\n'.join(txt)

    minimum_DG = 3
    pretty_name = 'Exponential-M4'
    model_name = 'Exponential'
    dtype = 'C'
    exe = 'exponential'
    exe_plot = 'Expo_CPlot'
    js_formula = "{a} * ({c}-({c}-1) * Math.exp(-1.*{b}*x))"
    exp_run_settings = ' 0 0010 33 0 1'
    js_parameters = ['a', 'b', 'c']
    version = 1.7
    date = '12/10/2009'
    defaults = {
        'bmdl_curve_calculation':   {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'append_or_overwrite':      {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'smooth_option':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'max_iterations':           {'c': 'op', 't': 'i', 'f': 0, 'd': 250, 'n': 'Iteration'},
        'relative_fn_conv':         {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Relative Function'},
        'parameter_conv':           {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Parameter'},
        'alpha':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Alpha'},
        'rho':                      {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Rho'},
        'a':                        {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'a'},
        'b':                        {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'b'},
        'c':                        {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'c'},
        'd':                        {'c': 'p',  't': 'p', 'f': 1, 'd': 'd|', 'n': 'd'},
        'bmd_calculation':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'BMD Calculation'},
        'bmdl_curve_calc':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 0, 'n': 'BMDL Curve Calculation'},
        'dose_drop':                {'c': 'ot', 't': 'dd', 'f': 0, 'd': 0, 'n': 'Doses to drop'},
        'bmr':                      {'c': 'b',  't': 'd', 'f': 1, 'd': 1.0},
        'bmr_type':                 {'c': 'b',  't': 'i', 'f': 1, 'd': 1},
        'confidence_level':         {'c': 'b',  't': 'd', 'f': 1, 'd': 0.95},
        'constant_variance':        {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'Constant Variance'}}
    possible_bmr = ('Abs. Dev.', 'Std. Dev.', 'Rel. Dev.', 'Point', 'Extra')
    output_prefix = 'M4'


class Exponential_M4_19(Exponential_M4_17):
    version = 1.9
    date = '01/29/2013'
    defaults = Exponential_M4_17.defaults.copy()
    defaults['max_iterations']['d'] = 500


class Exponential_M5_17(BMDModel):

    def dfile_print(self, dataset):
        """
        Custom function for printing exponential dfiles.
        """
        txt = self._dfile_print_header()
        txt.append('1 ' + str(dataset['numDG'] - self.values['dose_drop'][0]) + self.exp_run_settings)
        p = ('max_iterations', 'relative_fn_conv', 'parameter_conv',
             'bmdl_curve_calculation', 'bmd_calculation',
             'append_or_overwrite', 'smooth_option')
        txt.append(self._dfile_print_options(p))
        p = ('bmr_type', 'bmr', 'constant_variance', 'confidence_level')
        txt.append(self._dfile_print_options(p))
        p = ('alpha', 'rho', 'a', 'b', 'c', 'd')
        v = self._dfile_print_parameters(p)
        txt.append('\n'.join([v for i in xrange(4)]))
        txt.append(self._dfile_print_continuous_dataset(dataset))
        return '\n'.join(txt)

    minimum_DG = 4
    pretty_name = 'Exponential-M5'
    model_name = 'Exponential'
    dtype = 'C'
    exe = 'exponential'
    exe_plot = 'Expo_CPlot'
    js_formula = "{a} * ({c}-({c}-1) *  Math.exp(-1.*Math.pow({b}*x,{d})))"
    exp_run_settings = ' 0 0001 44 0 1'
    js_parameters = ['a', 'b', 'c', 'd']
    version = 1.7
    date = '12/10/2009'
    defaults = {
        'bmdl_curve_calculation':   {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'append_or_overwrite':      {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'smooth_option':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'max_iterations':           {'c': 'op', 't': 'i', 'f': 0, 'd': 250, 'n': 'Iteration'},
        'relative_fn_conv':         {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Relative Function'},
        'parameter_conv':           {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Parameter'},
        'alpha':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Alpha'},
        'rho':                      {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Rho'},
        'a':                        {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'a'},
        'b':                        {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'b'},
        'c':                        {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'c'},
        'd':                        {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'd'},
        'bmd_calculation':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'BMD Calculation'},
        'bmdl_curve_calc':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 0, 'n': 'BMDL Curve Calculation'},
        'dose_drop':                {'c': 'ot', 't': 'dd', 'f': 0, 'd': 0, 'n': 'Doses to drop'},
        'bmr':                      {'c': 'b',  't': 'd', 'f': 1, 'd': 1.0},
        'bmr_type':                 {'c': 'b',  't': 'i', 'f': 1, 'd': 1},
        'confidence_level':         {'c': 'b',  't': 'd', 'f': 1, 'd': 0.95},
        'constant_variance':        {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'Constant Variance'}}
    possible_bmr = ('Abs. Dev.', 'Std. Dev.', 'Rel. Dev.', 'Point', 'Extra')
    output_prefix = 'M5'


class Exponential_M5_19(Exponential_M5_17):
    version = 1.9
    date = '01/29/2013'
    defaults = Exponential_M5_17.defaults.copy()
    defaults['max_iterations']['d'] = 500


class Power_216(BMDModel):
    def dfile_print(self, dataset):
        """Custom file for printing dfile, using helper functions for BMD
        parent class."""
        txt = self._dfile_print_header()
        txt.append('1 ' + str(dataset['numDG'] - self.values['dose_drop'][0]) + ' 0')
        p = ('max_iterations', 'relative_fn_conv', 'parameter_conv',
             'bmdl_curve_calculation', 'restrict_power',
             'bmd_calculation', 'append_or_overwrite', 'smooth_option')
        txt.append(self._dfile_print_options(p))
        p = ('bmr_type', 'bmr', 'constant_variance', 'confidence_level')
        txt.append(self._dfile_print_options(p))
        p = ('alpha', 'rho', 'control', 'slope', 'power')
        txt.append(self._dfile_print_parameters(p))
        txt.append(self._dfile_print_continuous_dataset(dataset))
        return '\n'.join(txt)

    minimum_DG = 3
    model_name = 'Power'
    dtype = 'C'
    exe = 'power'
    exe_plot = '00power'
    js_formula = "{control} + {slope} * Math.pow(x,{power})"
    js_parameters = ['control', 'slope', 'power']
    version = 2.16
    date = '10/28/2009'
    defaults = {
        'bmdl_curve_calculation':   {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'append_or_overwrite':      {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'smooth_option':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'log_transform':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'max_iterations':           {'c': 'op', 't': 'i', 'f': 0, 'd': 250, 'n': 'Iteration'},
        'relative_fn_conv':         {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Relative Function'},
        'parameter_conv':           {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Parameter'},
        'alpha':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Alpha'},
        'rho':                      {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Rho'},
        'control':                  {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Control'},
        'slope':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Slope'},
        'power':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Power'},
        'restrict_power':           {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'Restrict Power'},
        'bmd_calculation':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'BMD Calculation'},
        'bmdl_curve_calc':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 0, 'n': 'BMDL Curve Calculation'},
        'dose_drop':                {'c': 'ot', 't': 'dd', 'f': 0, 'd': 0, 'n': 'Doses to drop'},
        'bmr':                      {'c': 'b',  't': 'd', 'f': 1, 'd': 1.0},
        'bmr_type':                 {'c': 'b',  't': 'i', 'f': 1, 'd': 1},
        'confidence_level':         {'c': 'b',  't': 'd', 'f': 1, 'd': 0.95},
        'constant_variance':        {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'Constant Variance'}}
    possible_bmr = ('Abs. Dev.', 'Std. Dev.', 'Rel. Dev.', 'Point', 'Extra')


class Power_217(Power_216):
    version = 2.17
    date = '01/28/2013'
    defaults = Power_216.defaults.copy()
    defaults['max_iterations']['d'] = 500


class Hill_216(BMDModel):
    def dfile_print(self, dataset):
        """Custom file for printing dfile, using helper functions for BMD
        parent class."""
        txt = self._dfile_print_header()
        txt.append('1 ' + str(dataset['numDG'] - self.values['dose_drop'][0]) + ' 0')
        p = ('max_iterations', 'relative_fn_conv', 'parameter_conv',
             'bmdl_curve_calculation', 'restrict_n',
             'bmd_calculation', 'append_or_overwrite', 'smooth_option')
        txt.append(self._dfile_print_options(p))
        p = ('bmr_type', 'bmr', 'constant_variance', 'confidence_level')
        txt.append(self._dfile_print_options(p))
        p = ('alpha', 'rho', 'intercept', 'v', 'n', 'k')
        txt.append(self._dfile_print_parameters(p))
        txt.append(self._dfile_print_continuous_dataset(dataset))
        return '\n'.join(txt)

    minimum_DG = 4
    model_name = 'Hill'
    dtype = 'C'
    exe = 'hill'
    exe_plot = '00Hill'
    js_formula = "{intercept} + ({v}*Math.pow(x,{n})) / (Math.pow({k},{n}) + Math.pow(x,{n}))"
    js_parameters = ['intercept', 'v', 'n', 'k']
    version = 2.16
    date = '04/06/2011'
    defaults = {
        'bmdl_curve_calculation':   {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'append_or_overwrite':      {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'smooth_option':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'log_transform':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'max_iterations':           {'c': 'op', 't': 'i', 'f': 0, 'd': 250, 'n': 'Iteration'},
        'relative_fn_conv':         {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Relative Function'},
        'parameter_conv':           {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Parameter'},
        'alpha':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Alpha'},
        'rho':                      {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Rho'},
        'intercept':                {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Intercept'},
        'v':                        {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'V'},
        'n':                        {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'N'},
        'k':                        {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'K'},
        'restrict_n':               {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'Restrict N>1'},
        'bmd_calculation':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'BMD Calculation'},
        'bmdl_curve_calc':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 0, 'n': 'BMDL Curve Calculation'},
        'dose_drop':                {'c': 'ot', 't': 'dd', 'f': 0, 'd': 0, 'n': 'Doses to drop'},
        'bmr':                      {'c': 'b',  't': 'd', 'f': 1, 'd': 1.0},
        'bmr_type':                 {'c': 'b',  't': 'i', 'f': 1, 'd': 1},
        'confidence_level':         {'c': 'b',  't': 'd', 'f': 1, 'd': 0.95},
        'constant_variance':        {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'Constant Variance'}}
    possible_bmr = ('Abs. Dev.', 'Std. Dev.', 'Rel. Dev.', 'Point', 'Extra')


class Hill_217(Hill_216):
    version = 2.17
    date = '01/28/2013'
    defaults = Hill_216.defaults.copy()
    defaults['max_iterations']['d'] = 500


#Dichotomous-Cancer Model Setup
class MultistageCancer_19(BMDModel):

    def dfile_print(self, dataset):
        """Custom file for printing dfile, using helper functions for BMD
        parent class."""
        txt = self._dfile_print_header()
        degree_poly = self.values['degree_poly'][0]
        txt.append(str(dataset['numDG'] - self.values['dose_drop'][0]) +
                   ' ' + str(degree_poly))
        p = ('max_iterations', 'relative_fn_conv', 'parameter_conv',
             'bmdl_curve_calculation', 'restrict_beta',
             'bmd_calculation', 'append_or_overwrite', 'smooth_option')
        txt.append(self._dfile_print_options(p))
        p = ('bmr', 'bmr_type', 'confidence_level')
        txt.append(self._dfile_print_options(p))
        p = ['background']
        for i in xrange(1, degree_poly + 1):
            p.append('beta' + str(i))
        txt.append(self._dfile_print_parameters(p))
        txt.append(self._dfile_print_dichotomous_dataset(dataset))
        return '\n'.join(txt)

    #todo: add check that degree poly must be <=8
    minimum_DG = 2
    model_name = 'Multistage-Cancer'
    dtype = 'DC'
    exe = 'cancer'
    exe_plot = '10cancer'
    js_formula = "{Background} + (1. - {Background}) * (1. - Math.exp( -1. * {Beta(1)}*x - {Beta(2)}*Math.pow(x,2) - {Beta(3)}*Math.pow(x,3) - {Beta(4)}*Math.pow(x,4) - {Beta(5)}*Math.pow(x,5) - {Beta(6)}*Math.pow(x,6) - {Beta(7)}*Math.pow(x,7) - {Beta(8)}*Math.pow(x,8)))"
    js_parameters = ['Background', 'Beta(1)', 'Beta(2)', 'Beta(3)', 'Beta(4)', 'Beta(5)', 'Beta(6)', 'Beta(7)', 'Beta(8)']
    version = 1.9
    date = '05/26/2010'
    defaults = {
        'bmdl_curve_calculation':   {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'append_or_overwrite':      {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'smooth_option':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'max_iterations':           {'c': 'op', 't': 'i', 'f': 0, 'd': 250, 'n': 'Iteration'},
        'relative_fn_conv':         {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Relative Function'},
        'parameter_conv':           {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Parameter'},
        'background':               {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Background'},
        'beta1':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta1'},
        'beta2':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta2'},
        'beta3':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta3'},
        'beta4':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta4'},
        'beta5':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta5'},
        'beta6':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta6'},
        'beta7':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta7'},
        'beta8':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta8'},
        'restrict_beta':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 1, 'n': 'Restrict Beta'},
        'degree_poly':              {'c': 'ot', 't': 'i', 'f': 0, 'd': 2, 'n': 'Degree of Polynomial'},
        'bmd_calculation':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'BMD Calculation'},
        'bmdl_curve_calc':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 0, 'n': 'BMDL Curve Calculation'},
        'dose_drop':                {'c': 'ot', 't': 'dd', 'f': 0, 'd': 0, 'n': 'Doses to drop'},
        'bmr':                      {'c': 'b',  't': 'i', 'f': 1, 'd': 0.1},
        'bmr_type':                 {'c': 'b',  't': 'd', 'f': 1, 'd': 0},
        'confidence_level':         {'c': 'b',  't': 'd', 'f': 1, 'd': 0.95}}
    possible_bmr = ('Extra', 'Added')


class MultistageCancer_110(MultistageCancer_19):
    version = 1.10
    date = '02/28/2013'
    defaults = MultistageCancer_19.defaults.copy()
    defaults['max_iterations']['d'] = 500


#Dichotomous Model Setup
class DichotomousHill_12(BMDModel):

    #TODO: Dichotmous Hill Function - look at source code or request d file format from JG?
    bmd_type = 'D'
    exe = 'DichoHill'
    version = 1.2
    date = '08/05/2011'
    possible_bmr = ('Extra', 'Added')
    minimum_DG = 4


class Multistage_32(BMDModel):

    def dfile_print(self, dataset):
        """Custom file for printing dfile, using helper functions for BMD
        parent class."""
        txt = self._dfile_print_header()
        degree_poly = self.values['degree_poly'][0]
        txt.append(str(dataset['numDG'] - self.values['dose_drop'][0]) +
                   ' ' + str(degree_poly))
        p = ('max_iterations', 'relative_fn_conv', 'parameter_conv',
             'bmdl_curve_calculation', 'restrict_beta',
             'bmd_calculation', 'append_or_overwrite', 'smooth_option')
        txt.append(self._dfile_print_options(p))
        p = ('bmr', 'bmr_type', 'confidence_level')
        txt.append(self._dfile_print_options(p))
        p = ['background']
        for i in xrange(1, degree_poly + 1):
            p.append('beta' + str(i))
        txt.append(self._dfile_print_parameters(p))
        txt.append(self._dfile_print_dichotomous_dataset(dataset))
        return '\n'.join(txt)

    #todo: add check that degree poly must be <=8
    minimum_DG = 2
    model_name = 'Multistage'
    dtype = 'D'
    exe = 'multistage'
    exe_plot = '10multista'
    js_formula = "{Background} + (1. - {Background}) * (1. - Math.exp( -1. * {Beta(1)}*x - {Beta(2)}*Math.pow(x,2) - {Beta(3)}*Math.pow(x,3) - {Beta(4)}*Math.pow(x,4) - {Beta(5)}*Math.pow(x,5) - {Beta(6)}*Math.pow(x,6) - {Beta(7)}*Math.pow(x,7) - {Beta(8)}*Math.pow(x,8)))"
    js_parameters = ['Background', 'Beta(1)', 'Beta(2)', 'Beta(3)', 'Beta(4)', 'Beta(5)', 'Beta(6)', 'Beta(7)', 'Beta(8)']
    version = 3.2
    date = '05/26/2010'
    defaults = {
        'bmdl_curve_calculation':   {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'append_or_overwrite':      {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'smooth_option':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'max_iterations':           {'c': 'op', 't': 'i', 'f': 0, 'd': 250, 'n': 'Iteration'},
        'relative_fn_conv':         {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Relative Function'},
        'parameter_conv':           {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Parameter'},
        'background':               {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Background'},
        'beta1':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta1'},
        'beta2':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta2'},
        'beta3':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta3'},
        'beta4':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta4'},
        'beta5':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta5'},
        'beta6':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta6'},
        'beta7':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta7'},
        'beta8':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Beta8'},
        'restrict_beta':            {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'Restrict Beta'},
        'degree_poly':              {'c': 'ot', 't': 'i', 'f': 0, 'd': 2, 'n': 'Degree of Polynomial'},
        'bmd_calculation':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'BMD Calculation'},
        'bmdl_curve_calc':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 0, 'n': 'BMDL Curve Calculation'},
        'dose_drop':                {'c': 'ot', 't': 'dd', 'f': 0, 'd': 0, 'n': 'Doses to drop'},
        'bmr':                      {'c': 'b',  't': 'i', 'f': 1, 'd': 0.1},
        'bmr_type':                 {'c': 'b',  't': 'd', 'f': 1, 'd': 0},
        'confidence_level':         {'c': 'b',  't': 'd', 'f': 1, 'd': 0.95}}
    possible_bmr = ('Extra', 'Added')


class Multistage_33(Multistage_32):
    version = 3.3
    date = '02/28/2013'
    defaults = Multistage_32.defaults.copy()
    defaults['max_iterations']['d'] = 500


class Weibull_215(BMDModel):

    def dfile_print(self, dataset):
        """Custom file for printing dfile, using helper functions for BMD
        parent class."""
        txt = self._dfile_print_header()
        txt.append(str(dataset['numDG'] - self.values['dose_drop'][0]))
        p = ('max_iterations', 'relative_fn_conv', 'parameter_conv',
             'bmdl_curve_calculation', 'restrict_power',
             'bmd_calculation', 'append_or_overwrite', 'smooth_option')
        txt.append(self._dfile_print_options(p))
        p = ('bmr', 'bmr_type', 'confidence_level')
        txt.append(self._dfile_print_options(p))
        p = ('background', 'slope', 'power')
        txt.append(self._dfile_print_parameters(p))
        txt.append(self._dfile_print_dichotomous_dataset(dataset))
        return '\n'.join(txt)

    minimum_DG = 3
    model_name = 'Weibull'
    dtype = 'D'
    exe = 'weibull'
    exe_plot = '10weibull'
    js_formula = "{Background} + (1-{Background}) * (1 - Math.exp( -1.*{Slope} * Math.pow(x,{Power}) ))"
    js_parameters = ['Background', 'Slope', 'Power']
    version = 2.15
    date = '10/28/2009'
    defaults = {
        'bmdl_curve_calculation':   {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'append_or_overwrite':      {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'smooth_option':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'log_transform':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'max_iterations':           {'c': 'op', 't': 'i', 'f': 0, 'd': 250, 'n': 'Iteration'},
        'relative_fn_conv':         {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Relative Function'},
        'parameter_conv':           {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Parameter'},
        'background':               {'c': 'p',  't': 'p', 'f': 1, 'd': 'd|'},
        'slope':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Slope'},
        'power':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Power'},
        'restrict_power':           {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'Restrict Power'},
        'bmd_calculation':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'BMD Calculation'},
        'bmdl_curve_calc':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 0, 'n': 'BMDL Curve Calculation'},
        'dose_drop':                {'c': 'ot', 't': 'dd', 'f': 0, 'd': 0, 'n': 'Doses to drop'},
        'bmr':                      {'c': 'b',  't': 'i', 'f': 1, 'd': 0.1},
        'bmr_type':                 {'c': 'b',  't': 'd', 'f': 1, 'd': 0},
        'confidence_level':         {'c': 'b',  't': 'd', 'f': 1, 'd': 0.95}}
    possible_bmr = ('Extra', 'Added')


class Weibull_216(Weibull_215):
    version = 2.16
    date = '02/28/2013'
    defaults = Weibull_215.defaults.copy()
    defaults['max_iterations']['d'] = 500


class LogProbit_32(BMDModel):

    def dfile_print(self, dataset):
        """Custom file for printing dfile, using helper functions for BMD
        parent class."""
        txt = self._dfile_print_header()
        txt.append(str(dataset['numDG'] - self.values['dose_drop'][0]))
        p = ('max_iterations', 'relative_fn_conv', 'parameter_conv',
             'bmdl_curve_calculation', 'log_transform', 'restrict_slope',
             'bmd_calculation', 'append_or_overwrite', 'smooth_option')
        txt.append(self._dfile_print_options(p))
        p = ('bmr', 'bmr_type', 'confidence_level')
        txt.append(self._dfile_print_options(p))
        p = ('background', 'slope', 'intercept')
        txt.append(self._dfile_print_parameters(p))
        txt.append(self._dfile_print_dichotomous_dataset(dataset))
        return '\n'.join(txt)

    minimum_DG = 3
    model_name = 'LogProbit'
    dtype = 'D'
    exe = 'probit'
    exe_plot = '10probit'
    js_formula = "{background} + (1-{background}) * Math.normalcdf(0,1,{intercept} + {slope}*Math.log(x))"
    js_parameters = ['background', 'intercept', 'slope']
    version = 3.2
    date = '10/28/2009'
    defaults = {
        'bmdl_curve_calculation':   {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'append_or_overwrite':      {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'smooth_option':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'log_transform':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 1},
        'max_iterations':           {'c': 'op', 't': 'i', 'f': 0, 'd': 250, 'n': 'Iteration'},
        'relative_fn_conv':         {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Relative Function'},
        'parameter_conv':           {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Parameter'},
        'background':               {'c': 'p',  't': 'p', 'f': 1, 'd': 'd|'},
        'slope':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Slope'},
        'intercept':                {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Intercept'},
        'restrict_slope':           {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'Restrict Slope'},
        'bmd_calculation':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'BMD Calculation'},
        'bmdl_curve_calc':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 0, 'n': 'BMDL Curve Calculation'},
        'dose_drop':                {'c': 'ot', 't': 'dd', 'f': 0, 'd': 0, 'n': 'Doses to drop'},
        'bmr':                      {'c': 'b',  't': 'i', 'f': 1, 'd': 0.1},
        'bmr_type':                 {'c': 'b',  't': 'd', 'f': 1, 'd': 0},
        'confidence_level':         {'c': 'b',  't': 'd', 'f': 1, 'd': 0.95}}
    possible_bmr = ('Extra', 'Added')


class LogProbit_33(LogProbit_32):
    version = 3.3
    date = '02/28/2013'
    defaults = LogProbit_32.defaults.copy()
    defaults['max_iterations']['d'] = 500


class Probit_32(BMDModel):

    def dfile_print(self, dataset):
        """Custom file for printing dfile, using helper functions for BMD
        parent class."""
        txt = self._dfile_print_header()
        txt.append(str(dataset['numDG'] - self.values['dose_drop'][0]))
        p = ('max_iterations', 'relative_fn_conv', 'parameter_conv',
             'bmdl_curve_calculation', 'log_transform', 'restrict_slope',
             'bmd_calculation', 'append_or_overwrite', 'smooth_option')
        txt.append(self._dfile_print_options(p))
        p = ('bmr', 'bmr_type', 'confidence_level')
        txt.append(self._dfile_print_options(p))
        p = ('background', 'slope', 'intercept')
        txt.append(self._dfile_print_parameters(p))
        txt.append(self._dfile_print_dichotomous_dataset(dataset))
        return '\n'.join(txt)

    minimum_DG = 2
    model_name = 'Probit'
    dtype = 'D'
    exe = 'probit'
    exe_plot = '10probit'
    js_formula = "Math.normalcdf(0,1,{intercept} + {slope}*x)"
    js_parameters = ['intercept', 'slope']
    version = 3.2
    date = '10/28/2009'
    defaults = {
        'bmdl_curve_calculation':   {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'append_or_overwrite':      {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'smooth_option':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'log_transform':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'restrict_slope':           {'c': 'ot', 't': 'b', 'f': 1, 'd': 0, 'n': 'Restrict Slope'},
        'max_iterations':           {'c': 'op', 't': 'i', 'f': 0, 'd': 250, 'n': 'Iteration'},
        'relative_fn_conv':         {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Relative Function'},
        'parameter_conv':           {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Parameter'},
        'background':               {'c': 'p',  't': 'p', 'f': 1, 'd': 'd|'},
        'slope':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Slope'},
        'intercept':                {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Intercept'},
        'bmd_calculation':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'BMD Calculation'},
        'bmdl_curve_calc':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 0, 'n': 'BMDL Curve Calculation'},
        'dose_drop':                {'c': 'ot', 't': 'dd', 'f': 0, 'd': 0, 'n': 'Doses to drop'},
        'bmr':                      {'c': 'b',  't': 'i', 'f': 1, 'd': 0.1},
        'bmr_type':                 {'c': 'b',  't': 'd', 'f': 1, 'd': 0},
        'confidence_level':         {'c': 'b',  't': 'd', 'f': 1, 'd': 0.95}}
    possible_bmr = ('Extra', 'Added')


class Probit_33(Probit_32):
    version = 3.3
    date = '02/28/2013'
    defaults = Probit_32.defaults.copy()
    defaults['max_iterations']['d'] = 500


class Gamma_215(BMDModel):

    def dfile_print(self, dataset):
        """Custom file for printing dfile, using helper functions for BMD
        parent class."""
        txt = self._dfile_print_header()
        txt.append(str(dataset['numDG'] - self.values['dose_drop'][0]))
        p = ('max_iterations', 'relative_fn_conv', 'parameter_conv',
             'bmdl_curve_calculation', 'restrict_power',
             'bmd_calculation', 'append_or_overwrite', 'smooth_option')
        txt.append(self._dfile_print_options(p))
        p = ('bmr', 'bmr_type', 'confidence_level')
        txt.append(self._dfile_print_options(p))
        p = ('background', 'slope', 'power')
        txt.append(self._dfile_print_parameters(p))
        txt.append(self._dfile_print_dichotomous_dataset(dataset))
        return '\n'.join(txt)

    minimum_DG = 3
    model_name = 'Gamma'
    dtype = 'D'
    exe = 'gamma'
    exe_plot = '10gammhit'
    js_formula = "{Background} + (1 - {Background}) * Math.GammaCDF(x*{Slope},{Power})"
    js_parameters = ['Background', 'Slope', 'Power']
    version = 2.15
    date = '10/28/2009'
    defaults = {
        'bmdl_curve_calculation':   {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'append_or_overwrite':      {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'smooth_option':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'max_iterations':           {'c': 'op', 't': 'i', 'f': 0, 'd': 250, 'n': 'Iteration'},
        'relative_fn_conv':         {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Relative Function'},
        'parameter_conv':           {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Parameter'},
        'background':               {'c': 'p',  't': 'p', 'f': 1, 'd': 'd|'},
        'slope':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Slope'},
        'power':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Power'},
        'bmd_calculation':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'BMD Calculation'},
        'restrict_power':           {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'Restrict Power'},
        'bmdl_curve_calc':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 0, 'n': 'BMDL Curve Calculation'},
        'dose_drop':                {'c': 'ot', 't': 'dd', 'f': 0, 'd': 0, 'n': 'Doses to drop'},
        'bmr':                      {'c': 'b',  't': 'i', 'f': 1, 'd': 0.1},
        'bmr_type':                 {'c': 'b',  't': 'd', 'f': 1, 'd': 0},
        'confidence_level':         {'c': 'b',  't': 'd', 'f': 1, 'd': 0.95}}
    possible_bmr = ('Extra', 'Added')


class Gamma_216(Gamma_215):
    version = 2.16
    date = '02/28/2013'
    defaults = Gamma_215.defaults.copy()
    defaults['max_iterations']['d'] = 500


class LogLogistic_213(BMDModel):

    def dfile_print(self, dataset):
        """Custom file for printing dfile, using helper functions for BMD
        parent class."""
        txt = self._dfile_print_header()
        txt.append(str(dataset['numDG'] - self.values['dose_drop'][0]))
        p = ('max_iterations', 'relative_fn_conv', 'parameter_conv',
             'bmdl_curve_calculation', 'log_transform', 'restrict_slope',
             'bmd_calculation', 'append_or_overwrite', 'smooth_option')
        txt.append(self._dfile_print_options(p))
        p = ('bmr', 'bmr_type', 'confidence_level')
        txt.append(self._dfile_print_options(p))
        p = ('background', 'slope', 'intercept')
        txt.append(self._dfile_print_parameters(p))
        txt.append(self._dfile_print_dichotomous_dataset(dataset))
        return '\n'.join(txt)

    minimum_DG = 3
    model_name = 'LogLogistic'
    dtype = 'D'
    exe = 'logist'
    exe_plot = '10logist'
    js_formula = "{background} + (1-{background})/( 1 + Math.exp(-1.*{intercept}-1.*{slope}*Math.log(x) ) )"
    js_parameters = ['background', 'intercept', 'slope']
    version = 2.13
    date = '10/28/2009'
    defaults = {
        'bmdl_curve_calculation':   {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'log_transform':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 1},
        'restrict_slope':           {'c': 'ot', 't': 'b', 'f': 1, 'd': 1},
        'append_or_overwrite':      {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'smooth_option':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'max_iterations':           {'c': 'op', 't': 'i', 'f': 0, 'd': 250, 'n': 'Iteration'},
        'relative_fn_conv':         {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Relative Function'},
        'parameter_conv':           {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Parameter'},
        'background':               {'c': 'p',  't': 'p', 'f': 1, 'd': 'd|'},
        'slope':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Slope'},
        'intercept':                {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Intercept'},
        'bmd_calculation':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'BMD Calculation'},
        'bmdl_curve_calc':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 0, 'n': 'BMDL Curve Calculation'},
        'dose_drop':                {'c': 'ot', 't': 'dd', 'f': 0, 'd': 0, 'n': 'Doses to drop'},
        'bmr':                      {'c': 'b',  't': 'i', 'f': 1, 'd': 0.1},
        'bmr_type':                 {'c': 'b',  't': 'd', 'f': 1, 'd': 0},
        'confidence_level':         {'c': 'b',  't': 'd', 'f': 1, 'd': 0.95}}
    possible_bmr = ('Extra', 'Added')


class LogLogistic_214(LogLogistic_213):
    version = 2.14
    date = '02/28/2013'
    defaults = LogLogistic_213.defaults.copy()
    defaults['max_iterations']['d'] = 500


class Logistic_213(BMDModel):

    def dfile_print(self, dataset):
        """Custom file for printing dfile, using helper functions for BMD
        parent class."""
        txt = self._dfile_print_header()
        txt.append(str(dataset['numDG'] - self.values['dose_drop'][0]))
        p = ('max_iterations', 'relative_fn_conv', 'parameter_conv',
             'bmdl_curve_calculation', 'log_transform', 'restrict_slope',
             'bmd_calculation', 'append_or_overwrite', 'smooth_option')
        txt.append(self._dfile_print_options(p))
        p = ('bmr', 'bmr_type', 'confidence_level')
        txt.append(self._dfile_print_options(p))
        p = ('background', 'slope', 'intercept')
        txt.append(self._dfile_print_parameters(p))
        txt.append(self._dfile_print_dichotomous_dataset(dataset))
        return '\n'.join(txt)

    minimum_DG = 2
    model_name = 'Logistic'
    dtype = 'D'
    exe = 'logist'
    exe_plot = '10logist'
    js_formula = "1/( 1 + Math.exp(-1*{intercept}-{slope}*x ))"
    js_parameters = ['intercept', 'slope']
    version = 2.13
    date = '10/28/2009'
    defaults = {
        'bmdl_curve_calculation':   {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'log_transform':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'restrict_slope':           {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'append_or_overwrite':      {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'smooth_option':            {'c': 'ot', 't': 'b', 'f': 1, 'd': 0},
        'max_iterations':           {'c': 'op', 't': 'i', 'f': 0, 'd': 250, 'n': 'Iteration'},
        'relative_fn_conv':         {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Relative Function'},
        'parameter_conv':           {'c': 'op', 't': 'd', 'f': 0, 'd': 1.0E-08, 'n': 'Parameter'},
        'background':               {'c': 'p',  't': 'p', 'f': 1, 'd': 'd|'},
        'slope':                    {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Slope'},
        'intercept':                {'c': 'p',  't': 'p', 'f': 0, 'd': 'd|', 'n': 'Intercept'},
        'bmd_calculation':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 1, 'n': 'BMD Calculation'},
        'bmdl_curve_calc':          {'c': 'ot', 't': 'b', 'f': 0, 'd': 0, 'n': 'BMDL Curve Calculation'},
        'dose_drop':                {'c': 'ot', 't': 'dd', 'f': 0, 'd': 0, 'n': 'Doses to drop'},
        'bmr':                      {'c': 'b',  't': 'i', 'f': 1, 'd': 0.1},
        'bmr_type':                 {'c': 'b',  't': 'd', 'f': 1, 'd': 0},
        'confidence_level':         {'c': 'b',  't': 'd', 'f': 1, 'd': 0.95}}
    possible_bmr = ('Extra', 'Added')


class Logistic_214(Logistic_213):
    version = 2.14
    date = '02/28/2013'
    defaults = Logistic_213.defaults.copy()
    defaults['max_iterations']['d'] = 500
