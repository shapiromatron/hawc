#usr/bin/python
import bmd_models
from os.path import join
from django.conf import settings


class BMDS_v230(object):
    model_path = join(settings.BMD_ROOT_PATH, 'BMDS230')
    temp_path = settings.TEMP_PATH
    models = {
        'D': {  # 'Dichotomous-Hill' : bmd_models.DichotomousHill_12, # todo: add
            'Weibull': bmd_models.Weibull_215,
            'LogProbit': bmd_models.LogProbit_32,
            'Probit': bmd_models.Probit_32,
            'Multistage': bmd_models.Multistage_32,
            'Gamma': bmd_models.Gamma_215,
            'Logistic': bmd_models.Logistic_213,
            'LogLogistic': bmd_models.LogLogistic_213},
        'DC': {
            'Multistage-Cancer': bmd_models.MultistageCancer_19},
        'C': {
            'Linear': bmd_models.Linear_216,
            'Polynomial': bmd_models.Polynomial_216,
            'Power': bmd_models.Power_216,
            'Exponential-M2': bmd_models.Exponential_M2_17,
            'Exponential-M3': bmd_models.Exponential_M3_17,
            'Exponential-M4': bmd_models.Exponential_M4_17,
            'Exponential-M5': bmd_models.Exponential_M5_17,
            'Hill': bmd_models.Hill_216,
        },
    }

    bmrs = {
        'D': [
            {'type': 'Extra', 'value': 0.1, 'confidence_level': 0.95},
            {'type': 'Added', 'value': 0.1, 'confidence_level': 0.95}],
        'DC': [
            {'type': 'Extra', 'value': 0.1, 'confidence_level': 0.95},
            {'type': 'Added', 'value': 0.1, 'confidence_level': 0.95}],
        'C': [
            {'type': 'Abs. Dev.', 'value': 0.1, 'confidence_level': 0.95},
            {'type': 'Std. Dev.', 'value': 1.0, 'confidence_level': 0.95},
            {'type': 'Rel. Dev.', 'value': 0.1, 'confidence_level': 0.95},
            {'type': 'Point', 'value': 1.0, 'confidence_level': 0.95},
            {'type': 'Extra', 'value': 1.0, 'confidence_level': 0.95}]
    }

    template_bmrs = {
        'D': [{'type': 'Extra', 'value': 0.1, 'confidence_level': 0.95}],
        'C': [{'type': 'Std. Dev.', 'value': 1.0, 'confidence_level': 0.95}],
        'DC': [{'type': 'Extra', 'value': 0.1, 'confidence_level': 0.95}]
    }

    template_models = {
        'D': ['Gamma', 'Logistic', 'LogLogistic', 'Probit', 'LogProbit', 'Weibull', 'Multistage'],
        'C': ['Exponential-M2', 'Exponential-M3', 'Exponential-M4', 'Exponential-M5', 'Power', 'Hill', 'Linear', 'Polynomial'],
        'DC': ['Multistage-Cancer']
    }


class BMDS_v231(BMDS_v230):
    model_path = join(settings.BMD_ROOT_PATH, 'BMDS231')


class BMDS_v240(BMDS_v231):
    model_path = join(settings.BMD_ROOT_PATH, 'BMDS240')
    models = {
        'D': {  # 'Dichotomous-Hill' : bmd_models.DichotomousHill_13, # todo: add
            'Weibull': bmd_models.Weibull_216,
            'LogProbit': bmd_models.LogProbit_33,
            'Probit': bmd_models.Probit_33,
            'Multistage': bmd_models.Multistage_33,
            'Gamma': bmd_models.Gamma_216,
            'Logistic': bmd_models.Logistic_214,
            'LogLogistic': bmd_models.LogLogistic_214},
        'DC': {
            'Multistage-Cancer': bmd_models.MultistageCancer_110},
        'C': {
            'Linear': bmd_models.Linear_217,
            'Polynomial': bmd_models.Polynomial_217,
            'Power': bmd_models.Power_217,
            'Exponential-M2': bmd_models.Exponential_M2_19,
            'Exponential-M3': bmd_models.Exponential_M3_19,
            'Exponential-M4': bmd_models.Exponential_M4_19,
            'Exponential-M5': bmd_models.Exponential_M5_19,
            'Hill': bmd_models.Hill_217,
        },
    }


class BMDS(object):
    versions = {
        '2.30': BMDS_v230,
        '2.31': BMDS_v231,
        '2.40': BMDS_v240
    }
