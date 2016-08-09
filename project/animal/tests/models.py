from unittest import skip

from django.core.exceptions import ValidationError
from django.test import TestCase

from assessment.models import Species, DoseUnits
from animal import models

from . import utils


class Experiment(TestCase):

    def setUp(self):
        utils.build_experiments_for_permission_testing(self)

    def test_is_generational(self):
        repro_exp = models.Experiment(
            study=self.study_working,
            name='experiment name',
            type='Rp',
            description='No description.')

        self.assertTrue(repro_exp.is_generational())

        nonrepro_exp = models.Experiment(
            study=self.study_working,
            name='experiment name',
            type='Ac',
            description='No description.')

        self.assertFalse(nonrepro_exp.is_generational())


class AnimalGroup(TestCase):

    def setUp(self):
        utils.build_animal_groups_for_permission_testing(self)

    def test_clean(self):
        new_species = Species.objects.create(name='foo')
        new_animal_group = models.AnimalGroup(
            experiment=self.experiment_working,
            name='animal group name',
            species=new_species,
            strain=self.strain,
            sex='M')

        with self.assertRaises(ValidationError) as err:
            new_animal_group.full_clean()

        self.assertItemsEqual(
            err.exception.messages,
            [u'Error- selected strain is not of the selected species.'])

    def test_get_assessment(self):
        self.assertEqual(
            self.assessment_working,
            self.animal_group_working.get_assessment())

    @skip("TODO: move to dosing-regime")
    def oldtest_get_doses_json(self):
        self.assertEqual(
            '[{"error": "no dosing regime"}]',
            self.animal_group_working.get_doses_json())

        self.dosing_regime_working = models.DosingRegime(
            dosed_animals=self.animal_group_working,
            route_of_exposure='I',
            description='foo')
        self.dosing_regime_working.save()
        utils.build_dose_units_for_permission_testing(self)

        self.dose_group_1 = models.DoseGroup.objects.create(
            dose_regime=self.dosing_regime_working,
            dose_units=self.dose_units,
            dose_group_id=0,
            dose=0.)
        self.dose_group_2 = models.DoseGroup.objects.create(
            dose_regime=self.dosing_regime_working,
            dose_units=self.dose_units,
            dose_group_id=1,
            dose=50.)
        self.assertEqual(
            '[{{"name": "mg/kg/day", "values": [0.0, 50.0], "id_": {0}}}]'.format(str(self.dose_units.pk)),
            self.animal_group_working.get_doses_json())


class DosingRegime(TestCase):

    def setUp(self):
        utils.build_dosing_regimes_for_permission_testing(self)

        self.alt_dose_units = DoseUnits.objects.create(name='mg/L')

        self.dose_group_1 = models.DoseGroup.objects.create(
            dose_regime=self.dosing_regime_working,
            dose_units=self.dose_units,
            dose_group_id=0,
            dose=0.)

        self.dose_group_2 = models.DoseGroup.objects.create(
            dose_regime=self.dosing_regime_working,
            dose_units=self.dose_units,
            dose_group_id=1,
            dose=50.)

        self.alt_dose_group_1 = models.DoseGroup.objects.create(
            dose_regime=self.dosing_regime_working,
            dose_units=self.alt_dose_units,
            dose_group_id=0,
            dose=100.)

        self.alt_dose_group_2 = models.DoseGroup.objects.create(
            dose_regime=self.dosing_regime_working,
            dose_units=self.alt_dose_units,
            dose_group_id=1,
            dose=150.)

    def test_dose_groups(self):
        self.assertTrue(len(self.dosing_regime_working.dose_groups) == 4)

    def test_get_doses_json(self):
        v = self.dosing_regime_working.get_doses_json(json_encode=False)
        self.assertEqual(v[0]['name'], 'mg/kg/day')
        self.assertItemsEqual(v[0]['values'], [0., 50.])
        self.assertEqual(v[1]['name'], 'mg/L')
        self.assertItemsEqual(v[1]['values'], [100, 150.])


class Endpoint(TestCase):
    def setUp(self):
        utils.build_endpoints_for_permission_testing(self)

    def test_dataset_increasing(self):
        self.assertEqual(self.endpoint_working.dataset_increasing, True)


class EndpointGroupPercentControl(TestCase):

    def _build_egdict(self, egs):
        output = []
        for eg in egs:
            output.append({
                "n": eg[1],
                "response": eg[2],
                "stdev": eg[3]
            })
        return output

    def _testerFactory(self, inputs, outputs, data_type):
        egs = self._build_egdict(inputs)
        models.EndpointGroup.percentControl(data_type, egs)
        for i, d in enumerate(outputs):
            self.assertAlmostEqual(egs[i]["percentControlMean"], d[0])
            self.assertAlmostEqual(egs[i]["percentControlLow"],  d[1])
            self.assertAlmostEqual(egs[i]["percentControlHigh"], d[2])

    def testIncreasing(self):
        inputs = [
            (0,   10, 15.1,  3.5),
            (100, 9,  25.5,  7.8),
            (200, 8,  35.7,  13.3),
            (300, 7,  150.1, 23.1),
        ]
        outputs = [
          (0.0, -20.3171209611, 20.3171209611),
          (68.8741721854, 27.3103479282, 110.437996443),
          (136.42384106, 66.5736748386, 206.274007281),
          (894.039735099, 711.728201234, 1076.35126896),
        ]
        self._testerFactory(inputs, outputs, "C")

    def testDecreasing(self):
        inputs = [
            (0,   7,  150.1, 15.1),
            (100, 8,  35.7,  13.3),
            (200, 9,  25.5,  7.8),
            (300, 10, 15.1,  3.5),
        ]
        outputs = [
            (0.0, -10.5394586484, 10.5394586484),
            (-76.2158560959, -82.6067710106, -69.8249411813),
            (-83.0113257828, -86.634786933, -79.3878646326),
            (-89.9400399734, -91.5681779063, -88.3119020404),
        ]
        self._testerFactory(inputs, outputs, "C")

    def testEdge(self):
        inputs = [
            (0,   7,   150.1, 15.1),
            (100, 7,   150.1, 15.1),
            (200, 700, 150.1, 15.1),
            (300, 10,  0,  15),
        ]
        outputs = [
            (0.0, -10.5394586484, 10.5394586484),
            (0.0, -10.5394586484, 10.5394586484),
            (0.0, -7.48969260009, 7.48969260009),
            (None, None, None),
        ]
        self._testerFactory(inputs, outputs, "C")

    def testNoneCases(self):
        inputs = [
          (0,   7,  150.1, None),
          (0,   7,  0,     3),
        ]
        outputs = [
            (0.0, None, None),
            (None, None, None),
        ]
        self._testerFactory(inputs, outputs, "C")

        inputs = [
          (0,   7,  0,     3),
          (0,   7,  150.1, None),
        ]
        outputs = [
            (None, None, None),
            (None, None, None),
        ]
        self._testerFactory(inputs, outputs, "C")

    def testPCases(self):
        egs = [{
          "response": 1,
          "lower_ci": 2,
          "upper_ci": 3
        }]
        models.EndpointGroup.percentControl("P", egs)
        self.assertAlmostEqual(egs[0]["percentControlMean"], 1)
        self.assertAlmostEqual(egs[0]["percentControlLow"],  2)
        self.assertAlmostEqual(egs[0]["percentControlHigh"], 3)
