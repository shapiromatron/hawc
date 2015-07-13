import json

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from animal.models import (Experiment, AnimalGroup,  Species, Strain,
                           DosingRegime, Endpoint, EndpointGroup,
                           UncertaintyFactorEndpoint, DoseUnits, DoseGroup, Aggregation)
from . import forms
from study.tests import build_studies_for_permission_testing

from utils.tests import FormTester


def build_experiments_for_permission_testing(obj):
    build_studies_for_permission_testing(obj)
    obj.experiment_working = Experiment(study=obj.study_working,
                                        name='experiment name',
                                        type='Ac',
                                        description='No description.')
    obj.experiment_working.save()

    obj.experiment_final = Experiment(study=obj.study_final,
                                      name='experiment name',
                                      type='Ac',
                                      description='No description.')
    obj.experiment_final.save()


def build_species_for_permission_testing(obj):
    obj.species = Species(name='orangutan')
    obj.species.save()


def build_strain_for_permission_testing(obj):
    obj.strain = Strain(name='asdf',
                        species=obj.species)
    obj.strain.save()


def build_animal_groups_for_permission_testing(obj):
    build_experiments_for_permission_testing(obj)
    build_species_for_permission_testing(obj)
    build_strain_for_permission_testing(obj)
    obj.animal_group_working = AnimalGroup(experiment=obj.experiment_working,
                                           name='animal group name',
                                           species=obj.species,
                                           strain=obj.strain,
                                           sex='M',
                                           dose_groups=4)
    obj.animal_group_working.save()

    obj.animal_group_final = AnimalGroup(experiment=obj.experiment_final,
                                         name='animal group name',
                                         species=obj.species,
                                         strain=obj.strain,
                                         sex='M',
                                         dose_groups=4)
    obj.animal_group_final.save()


def build_dose_units_for_permission_testing(obj):
    obj.dose_units = DoseUnits(units='mg/kg/day',
                               administered=True,
                               converted=True,
                               hed=True)
    obj.dose_units.save()


def build_dosing_regimes_for_permission_testing(obj):
    build_animal_groups_for_permission_testing(obj)
    build_dose_units_for_permission_testing(obj)
    obj.dosing_regime_working = DosingRegime(dosed_animals=obj.animal_group_working,
                                             route_of_exposure='I',
                                             description='foo')
    obj.dosing_regime_working.save()
    obj.animal_group_working.dosing_regime = obj.dosing_regime_working
    obj.animal_group_working.save()

    obj.dosing_regime_final = DosingRegime(dosed_animals=obj.animal_group_final,
                                           route_of_exposure='I',
                                           description='foo')
    obj.dosing_regime_final.save()
    obj.animal_group_final.dosing_regime = obj.dosing_regime_final
    obj.animal_group_final.save()


def build_endpoints_for_permission_testing(obj):
    build_dosing_regimes_for_permission_testing(obj)
    build_dose_groups(obj)
    obj.endpoint_working = Endpoint(assessment=obj.assessment_working,
                                    animal_group=obj.animal_group_working,
                                    name='endpoint name',
                                    response_units='% affected',
                                    data_type='C',
                                    NOEL=1,
                                    LOEL=-999)
    obj.endpoint_working.save()

    obj.endpoint_final = Endpoint(assessment=obj.assessment_final,
                                  animal_group=obj.animal_group_final,
                                  name='endpoint name',
                                  response_units='% affected',
                                  data_type='C',
                                  NOEL=-999,
                                  LOEL=-999)
    obj.endpoint_final.save()

    # now build endpoint groups
    endpoints = [obj.endpoint_working, obj.endpoint_final]
    egs = []
    for endpoint in endpoints:
        for i in xrange(4):
            egs.append(EndpointGroup(dose_group_id=i,
                                     n=20,
                                     incidence=None,
                                     response=i*5.,
                                     variance=i*1.,
                                     endpoint=endpoint))
    EndpointGroup.objects.bulk_create(egs)


def build_aggregations_for_permission_testing(obj):
    build_endpoints_for_permission_testing(obj)
    obj.aggregation_working = Aggregation(assessment=obj.assessment_working,
                                          name="foo",
                                          aggregation_type="CD",
                                          dose_units=obj.dose_units)
    obj.aggregation_working.save()
    obj.aggregation_working.endpoints.add(obj.endpoint_working)

    obj.aggregation_final = Aggregation(assessment=obj.assessment_final,
                                        name="foo",
                                        aggregation_type="CD",
                                        dose_units=obj.dose_units)
    obj.aggregation_final.save()
    obj.aggregation_final.endpoints.add(obj.endpoint_final)


def build_ufs_for_permission_testing(obj):
    build_endpoints_for_permission_testing(obj)
    obj.ufa_working = UncertaintyFactorEndpoint(endpoint=obj.endpoint_working,
                                        uf_type='UFA',
                                        value=10,
                                        description='')
    obj.ufa_working.save()

    obj.ufa_final = UncertaintyFactorEndpoint(endpoint=obj.endpoint_final,
                                      uf_type='UFA',
                                      value=10,
                                      description='')
    obj.ufa_final.save()


def build_dosing_datasets_json(dose_units):
    # build a DoseGroup dataset with four dose groups
    dose_groups = []
    for i in xrange(4):
        dose_groups.append({'dose_units': dose_units.pk,
                            'dose_group_id': i,
                            'dose': i*50})
    return json.dumps(dose_groups)


def build_dose_groups(obj):
    # build four dose-groups for each object
    regimes = [obj.dosing_regime_working, obj.dosing_regime_final]
    dgs = []
    for regime in regimes:
        for i in xrange(4):
            dgs.append(DoseGroup(dose_regime=regime,
                                 dose_units=obj.dose_units,
                                 dose_group_id=i,
                                 dose=i*50.))
    DoseGroup.objects.bulk_create(dgs)


class ExperimentPermissions(TestCase):
    """
    Ensure permissions for experiment views are properly configured.
    """
    def setUp(self):
        build_experiments_for_permission_testing(self)

    def test_read_success(self):
        clients = ['sudo', 'pm', 'team', 'rev']
        views = [
            reverse('animal:experiment_detail', kwargs={'pk': self.experiment_working.pk}),
            reverse('animal:experiment_detail', kwargs={'pk': self.experiment_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))
            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 200)

    def test_read_failure(self):
        #anonymous user
        c = Client()
        views = [
            {'view': reverse('animal:experiment_detail', kwargs={'pk': self.experiment_final.pk}), 'status': 200},
            {'view': reverse('animal:experiment_detail', kwargs={'pk': self.experiment_working.pk}), 'status': 403},
        ]
        for view in views:
            response = c.get(view['view'])
            self.assertTrue(response.status_code == view['status'])

    def test_crud_success(self):
        # check to ensure that sudo, pm and team can view the edit list,
        # create a new experiment, edit it, and delete it
        clients = ['sudo', 'pm', 'team']
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            #create new
            response = c.get(reverse('animal:experiment_new',
                             kwargs={'study': self.study_working.pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:experiment_new',
                              kwargs={'study': self.study_working.pk}),
                              {"name": 'experiment name',
                               "type": 'Ac',
                               "description": 'No description.'})
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('animal/experiment_detail.html')
            pk = Experiment.objects.all().latest('created').pk

            #edit
            response = c.get(reverse('animal:experiment_update',
                             kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:experiment_update',
                              kwargs={'pk': pk}),
                              {"name": 'experiment name 2',
                               "type": 'Ca',
                               "description": 'No descriptions.'})
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('animal/experiment_detail.html')

            #delete
            response = c.get(reverse('animal:experiment_delete',
                             kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:experiment_delete', kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('study/study_detail.html')

    def test_crud_failure(self):
        # make sure that reviewers and those not logged in have any access to
        # these CRUD views on an ongoing assessment
        clients = ['rev', None]
        views = [
            reverse('animal:experiment_update', kwargs={'pk': self.experiment_working.pk}),
            reverse('animal:experiment_new', kwargs={'study': self.study_working.pk}),
            reverse('animal:experiment_delete', kwargs={'pk': self.experiment_working.pk}),
            reverse('animal:experiment_update', kwargs={'pk': self.experiment_final.pk}),
            reverse('animal:experiment_new', kwargs={'study': self.study_final.pk}),
            reverse('animal:experiment_delete', kwargs={'pk': self.experiment_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 403)
                response = c.post(view)
                self.assertTrue(response.status_code in [403, 405])

        # test that no-one (except sudo) can change a final assessment
        clients = ['pm', 'team', 'rev', None]
        views = [
            reverse('animal:experiment_update', kwargs={'pk': self.experiment_final.pk}),
            reverse('animal:experiment_new', kwargs={'study': self.study_final.pk}),
            reverse('animal:experiment_delete', kwargs={'pk': self.experiment_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 403)
                response = c.post(view)
                self.assertTrue(response.status_code in [403, 405])


class ExperimentModelFunctionality(TestCase):
    """
    Check experiment object functionality.
    """
    def setUp(self):
        build_experiments_for_permission_testing(self)

    def test_is_generational(self):
        repro_exp = Experiment(study=self.study_working,
                               name='experiment name',
                               type='Rp',
                               description='No description.')

        self.assertTrue(repro_exp.is_generational())

        nonrepro_exp = Experiment(study=self.study_working,
                                  name='experiment name',
                                  type='Ac',
                                  description='No description.')

        self.assertFalse(nonrepro_exp.is_generational())


class AnimalGroupPermissions(TestCase):
    """
    Ensure permissions for animal-group views are properly configured.
    """
    def setUp(self):
        build_animal_groups_for_permission_testing(self)

    def test_read_success(self):
        clients = ['sudo', 'pm', 'team', 'rev']
        views = [
            reverse('animal:animal_group_detail', kwargs={'pk': self.animal_group_working.pk}),
            reverse('animal:animal_group_detail', kwargs={'pk': self.animal_group_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))
            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 200)

    def test_read_failure(self):
        #anonymous user
        c = Client()
        views = [
            {'view': reverse('animal:animal_group_detail', kwargs={'pk': self.animal_group_final.pk}), 'status': 200},
            {'view': reverse('animal:animal_group_detail', kwargs={'pk': self.animal_group_working.pk}), 'status': 403},
        ]
        for view in views:
            response = c.get(view['view'])
            self.assertTrue(response.status_code == view['status'])

    def test_crud_success(self):
        # check to ensure that sudo, pm and team can view the edit list,
        # create a new animal_group, edit it, and delete it
        clients = ['sudo', 'pm', 'team']
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            #create new
            response = c.get(reverse('animal:animal_group_new',
                             kwargs={'pk': self.experiment_working.pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:animal_group_new',
                              kwargs={'pk': self.experiment_working.pk}),
                               {"experiment": self.experiment_working.pk,
                                "name": 'animal group name',
                                "species": self.species.pk,
                                "strain": self.strain.pk,
                                "sex": 'M',
                                "dose_groups": 4})
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('animal/animal_group_detail.html')
            pk = AnimalGroup.objects.all().latest('created').pk

            #edit
            response = c.get(reverse('animal:animal_group_update',
                             kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:animal_group_update',
                              kwargs={'pk': pk}),
                              {"experiment": self.experiment_working.pk,
                               "name": 'animal group name',
                               "species": self.species.pk,
                               "strain": self.strain.pk,
                               "sex": 'M',
                               "dose_groups": 4})
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('animal/animal_group_detail.html')

            #delete
            response = c.get(reverse('animal:animal_group_delete',
                             kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:animal_group_delete', kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('animal/experiment_detail.html')

    def test_crud_failure(self):
        # make sure that reviewers and those not logged in have any access to
        # these CRUD views on an ongoing assessment
        clients = ['rev', None]
        views = [
            reverse('animal:animal_group_update', kwargs={'pk': self.animal_group_working.pk}),
            reverse('animal:animal_group_new', kwargs={'pk': self.experiment_working.pk}),
            reverse('animal:animal_group_delete', kwargs={'pk': self.animal_group_working.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 403)
                response = c.post(view)
                self.assertTrue(response.status_code in [403, 405])

        # test that no-one (except sudo) can change a final assessment
        clients = ['pm', 'team', 'rev', None]
        views = [
            reverse('animal:animal_group_new', kwargs={'pk': self.experiment_final.pk}),
            reverse('animal:animal_group_update', kwargs={'pk': self.animal_group_final.pk}),
            reverse('animal:animal_group_delete', kwargs={'pk': self.animal_group_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 403)
                response = c.post(view)
                self.assertTrue(response.status_code in [403, 405])


class AnimalGroupModelFunctionality(TestCase):
    """
    Check object functionality.
    """
    def setUp(self):
        build_animal_groups_for_permission_testing(self)

    def test_clean(self):
        new_species = Species(name='foo')
        new_species.save()
        new_animal_group = AnimalGroup(experiment=self.experiment_working,
                                       name='animal group name',
                                       species=new_species,
                                       strain=self.strain,
                                       sex='M',
                                       dose_groups=4)

        with self.assertRaises(ValidationError) as err:
            new_animal_group.full_clean()

        self.assertItemsEqual(err.exception.messages, [u'Error- selected strain is not of the selected species.'])

    def test_get_assessment(self):
        self.assertEqual(self.assessment_working, self.animal_group_working.get_assessment())

    def test_get_doses_json_a(self):
        # split get_doses_test because it caches the result in object instance
        self.assertEqual('[{"error": "no dosing regime"}]', self.animal_group_working.get_doses_json())

    def test_get_doses_json_b(self):
        # split get_doses_test because it caches the result in object instance
        self.dosing_regime_working = DosingRegime(dosed_animals=self.animal_group_working,
                                                  route_of_exposure='I',
                                                  description='foo')
        self.dosing_regime_working.save()
        build_dose_units_for_permission_testing(self)
        self.dose_group_1 = DoseGroup(dose_regime=self.dosing_regime_working,
                                      dose_units=self.dose_units,
                                      dose_group_id=0,
                                      dose=0.)
        self.dose_group_2 = DoseGroup(dose_regime=self.dosing_regime_working,
                                      dose_units=self.dose_units,
                                      dose_group_id=1,
                                      dose=50.)
        self.dose_group_1.save()
        self.dose_group_2.save()
        self.assertEqual('[{"units": "mg/kg/day", "values": [0.0, 50.0], "units_id": ' + str(self.dose_units.pk) + '}]', self.animal_group_working.get_doses_json())

class DosingRegimeModelFunctionality(TestCase):
    """
    Check object functionality.
    """
    def setUp(self):
        build_dosing_regimes_for_permission_testing(self)
        self.alt_dose_units = DoseUnits(units='mg/L',
                                        administered=True,
                                        converted=True,
                                        hed=True)
        self.alt_dose_units.save()
        self.dose_group_1 = DoseGroup(dose_regime=self.dosing_regime_working,
                                      dose_units=self.dose_units,
                                      dose_group_id=0,
                                      dose=0.)

        self.dose_group_2 = DoseGroup(dose_regime=self.dosing_regime_working,
                                      dose_units=self.dose_units,
                                      dose_group_id=1,
                                      dose=50.)
        self.dose_group_1.save()
        self.dose_group_2.save()
        self.alt_dose_group_1 = DoseGroup(dose_regime=self.dosing_regime_working,
                                          dose_units=self.alt_dose_units,
                                          dose_group_id=0,
                                          dose=100.)

        self.alt_dose_group_2 = DoseGroup(dose_regime=self.dosing_regime_working,
                                          dose_units=self.alt_dose_units,
                                          dose_group_id=1,
                                          dose=150.)
        self.alt_dose_group_1.save()
        self.alt_dose_group_2.save()

    def test_dose_groups(self):
        self.assertTrue(len(self.dosing_regime_working.dose_groups) == 4)

    def test_get_dose_groups(self):
        v = self.dosing_regime_working.get_dose_groups()
        self.assertEqual(v[0][0], self.dose_group_1)
        self.assertEqual(v[0][1], self.alt_dose_group_1)
        self.assertEqual(v[1][0], self.dose_group_2)
        self.assertEqual(v[1][1], self.alt_dose_group_2)

    def test_get_doses_json(self):
        v = self.dosing_regime_working.get_doses_json(json_encode=False)
        self.assertEqual(v[0]['units'], 'mg/kg/day')
        self.assertItemsEqual(v[0]['values'], [0., 50.])
        self.assertEqual(v[1]['units'], 'mg/L')
        self.assertItemsEqual(v[1]['values'], [100, 150.])


class DoseGroupModelFunctionality(TestCase):
    """
    Check object functionality.
    """
    def setUp(self):
        build_dosing_regimes_for_permission_testing(self)

    def test_clean_formset(self):
        #this should pass and not throw and error
        dose_groups = json.loads(build_dosing_datasets_json(self.dose_units))

        try:
            DoseGroup.clean_formset(dose_groups, 4)
        except:
            self.fail("Should have successfully been cleaned as a valid dose-set")

        with self.assertRaises(ValidationError) as err:
            DoseGroup.clean_formset(dose_groups, 3)

        self.assertItemsEqual(err.exception.messages, [u'<ul><li>Each dose-type must have 3 dose groups</li></ul>'])

        # now, add a new dose-units type
        dose_groups.append({'dose_regime': self.dosing_regime_working.pk,
                            'dose_units': 2,
                            'dose_group_id': 0,
                            'dose': 50.})
        with self.assertRaises(ValidationError) as err:
            DoseGroup.clean_formset(dose_groups, 4)

        self.assertItemsEqual(err.exception.messages, [u'<ul><li>Each dose-type must have 4 dose groups</li></ul>'])


class EndpointPermissions(TestCase):
    """
    Ensure endpoint for animal-group views are properly configured.
    """
    def setUp(self):
        build_endpoints_for_permission_testing(self)

    def test_read_success(self):
        clients = ['sudo', 'pm', 'team', 'rev']
        views = [
            reverse('animal:endpoint_list', kwargs={'pk': self.assessment_working.pk}),
            reverse('animal:endpoint_list', kwargs={'pk': self.assessment_final.pk}),
            reverse('animal:assessment_endpoint_search', kwargs={'pk': self.assessment_working.pk}),
            reverse('animal:assessment_endpoint_search', kwargs={'pk': self.assessment_final.pk}),
            reverse('animal:assessment_endpoint_search_query', kwargs={'pk': self.assessment_working.pk}),
            reverse('animal:assessment_endpoint_search_query', kwargs={'pk': self.assessment_final.pk}),
            reverse('animal:assessment_endpoint_taglist', kwargs={'pk': self.assessment_working.pk, 'tag_slug': 'foo'}),
            reverse('animal:assessment_endpoint_taglist', kwargs={'pk': self.assessment_final.pk, 'tag_slug': 'foo'}),
            reverse('animal:endpoint_detail', kwargs={'pk': self.endpoint_working.pk}),
            reverse('animal:endpoint_detail', kwargs={'pk': self.endpoint_final.pk}),
            reverse('animal:endpoint_json', kwargs={'pk': self.endpoint_working.pk}),
            reverse('animal:endpoint_json', kwargs={'pk': self.endpoint_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))
            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 200)

    def test_read_failure(self):
        #anonymous user
        c = Client()
        views = [
            {'view': reverse('animal:endpoint_list', kwargs={'pk': self.assessment_working.pk}), 'status': 403},
            {'view': reverse('animal:endpoint_list', kwargs={'pk': self.assessment_final.pk}), 'status': 200},
            {'view': reverse('animal:assessment_endpoint_search', kwargs={'pk': self.assessment_working.pk}), 'status': 403},
            {'view': reverse('animal:assessment_endpoint_search', kwargs={'pk': self.assessment_final.pk}), 'status': 200},
            {'view': reverse('animal:assessment_endpoint_search_query', kwargs={'pk': self.assessment_working.pk}), 'status': 403},
            {'view': reverse('animal:assessment_endpoint_search_query', kwargs={'pk': self.assessment_final.pk}), 'status': 200},
            {'view': reverse('animal:assessment_endpoint_taglist', kwargs={'pk': self.assessment_working.pk, 'tag_slug': 'foo'}), 'status': 403},
            {'view': reverse('animal:assessment_endpoint_taglist', kwargs={'pk': self.assessment_final.pk, 'tag_slug': 'foo'}), 'status': 200},
            {'view': reverse('animal:endpoint_detail', kwargs={'pk': self.endpoint_working.pk}), 'status': 403},
            {'view': reverse('animal:endpoint_detail', kwargs={'pk': self.endpoint_final.pk}), 'status': 200},
            {'view': reverse('animal:endpoint_json', kwargs={'pk': self.endpoint_working.pk}), 'status': 403},
            {'view': reverse('animal:endpoint_json', kwargs={'pk': self.endpoint_final.pk}), 'status': 200},
        ]
        for view in views:
            response = c.get(view['view'])
            self.assertTrue(response.status_code == view['status'])

    def test_crud_success(self):
        # check to ensure that sudo, pm and team can view the edit list,
        # create a new endpoint, edit it, and delete it
        clients = ['sudo', 'pm', 'team']
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            #create new
            response = c.get(reverse('animal:endpoint_new',
                             kwargs={'pk': self.animal_group_working.pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:endpoint_new',
                              kwargs={'pk': self.animal_group_working.pk}),
                                {"animal_group": self.animal_group_working.pk,
                                 "name": 'endpoint name',
                                 "response_units": '% affected',
                                 "data_type": 'D',
                                 "NOEL": 1,
                                 "LOEL": -999,
                                 "egs_json": '[{"dose_group_id":0,"n":20,"incidence":1,"response":null,"variance":null},{"dose_group_id":1,"n":20,"incidence":2,"response":null,"variance":null},{"dose_group_id":2,"n":20,"incidence":3,"response":null,"variance":null},{"dose_group_id":3,"n":20,"incidence":4,"response":null,"variance":null}]'})
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('animal/endpoint_detail.html')
            pk = Endpoint.objects.all().latest('created').pk

            #edit
            response = c.get(reverse('animal:endpoint_update',
                             kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:endpoint_update',
                              kwargs={'pk': pk}),
                                {"animal_group": self.animal_group_working.pk,
                                 "name": 'endpoint name',
                                 "response_units": '% affected',
                                 "data_type": 'D',
                                 "NOEL": 1,
                                 "LOEL": -999,
                                 "egs_json": '[{"dose_group_id":0,"n":20,"incidence":1,"response":null,"variance":null},{"dose_group_id":1,"n":20,"incidence":2,"response":null,"variance":null},{"dose_group_id":2,"n":20,"incidence":3,"response":null,"variance":null},{"dose_group_id":3,"n":20,"incidence":4,"response":null,"variance":null}]'})
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('animal/endpoint_detail.html')

            #delete
            response = c.get(reverse('animal:endpoint_delete',
                             kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:endpoint_delete', kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('animal/animal_group_detail.html')

    def test_crud_failure(self):
        # make sure that reviewers and those not logged in have any access to
        # these CRUD views on an ongoing assessment
        clients = ['rev', None]
        views = [
            reverse('animal:endpoint_update', kwargs={'pk': self.endpoint_working.pk}),
            reverse('animal:endpoint_new', kwargs={'pk': self.animal_group_working.pk}),
            reverse('animal:endpoint_delete', kwargs={'pk': self.endpoint_working.pk}),
            reverse('animal:endpoint_update', kwargs={'pk': self.endpoint_final.pk}),
            reverse('animal:endpoint_new', kwargs={'pk': self.animal_group_final.pk}),
            reverse('animal:endpoint_delete', kwargs={'pk': self.endpoint_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 403)
                response = c.post(view)
                self.assertTrue(response.status_code in [403, 405])

        # test that no-one (except sudo) can change a final assessment
        clients = ['pm', 'team', 'rev', None]
        views = [
            reverse('animal:endpoint_update', kwargs={'pk': self.endpoint_final.pk}),
            reverse('animal:endpoint_new', kwargs={'pk': self.animal_group_final.pk}),
            reverse('animal:endpoint_delete', kwargs={'pk': self.endpoint_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 403)
                response = c.post(view)
                self.assertTrue(response.status_code in [403, 405])


class EndpointFunctionality(TestCase):
    def setUp(self):
        build_endpoints_for_permission_testing(self)

    def test_dataset_increasing(self):
        self.assertEqual(self.endpoint_working.dataset_increasing, True)

    def bmds_session_exists(self):
        self.assertEqual(self.endpoint_working.bmds_session_exists(), False)

    def test_get_bmds_session(self):
        self.assertEqual(self.endpoint_working.get_bmds_session(), None)


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
        EndpointGroup.percentControl(data_type, egs)
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
            (-100.0, -106.193934924, -93.806065076),
        ]
        self._testerFactory(inputs, outputs, "C")

    def testNoneCases(self):
        nulls = [
          [(0,   7,  150.1, None), ],
          [(0,   7,  0,     3), ]
        ]
        for inputs in nulls:
          egs = self._build_egdict(inputs)
          EndpointGroup.percentControl("C", egs)
          self.assertAlmostEqual(egs[0]["percentControlMean"], None)
          self.assertAlmostEqual(egs[0]["percentControlLow"],  None)
          self.assertAlmostEqual(egs[0]["percentControlHigh"], None)

    def testPCases(self):
        egs = [{
          "response": 1,
          "lower_ci": 2,
          "upper_ci": 3
        }]
        EndpointGroup.percentControl("P", egs)
        self.assertAlmostEqual(egs[0]["percentControlMean"], 1)
        self.assertAlmostEqual(egs[0]["percentControlLow"],  2)
        self.assertAlmostEqual(egs[0]["percentControlHigh"], 3)


class ExperimentForm(FormTester):

    def setUp(self):
        self.Form = forms.ExperimentForm
        self.baseInps = {
            'name': 'Example',
            'type': 'Ac',
            'litter_effects': 'NA',
            'purity_available': False,
            'purity_qualifier': "",
            'purity': None
        }
        build_studies_for_permission_testing(self)

    def createTestForm(self, inps, *args, **kwargs):
        return self.Form(inps, parent=self.study_working)

    def test_valid_form(self):
        self.assertTrue(self.createTestForm(self.baseInps).is_valid())

    def test_purity(self):
        inps = self.baseInps.copy()

        inps.update(purity_available=True, purity=None, purity_qualifier="")
        self.fieldHasError(inps, "purity", self.Form.PURITY_REQ)
        self.fieldHasError(inps, "purity_qualifier", self.Form.PURITY_QUALIFIER_REQ)

        inps.update(purity_available=False, purity=95, purity_qualifier=">")
        self.fieldHasError(inps, "purity", self.Form.PURITY_NOT_REQ)
        self.fieldHasError(inps, "purity_qualifier", self.Form.PURITY_QUALIFIER_NOT_REQ)

    def test_litter_effects(self):
        inps = self.baseInps.copy()

        inps.update(type="Rp", litter_effects="NA")
        self.fieldHasError(inps, "litter_effects", self.Form.LIT_EFF_REQ)

        inps.update(type="Ac", litter_effects="NR")
        self.fieldHasError(inps, "litter_effects", self.Form.LIT_EFF_NOT_REQ)

        inps.update(type="Ac", litter_effects="NA", litter_effect_notes="Test")
        self.fieldHasError(inps, "litter_effect_notes",  self.Form.LIT_EFF_NOTES_NOT_REQ)

        inps.update(type="Rp", litter_effects="O", litter_effect_notes="")
        self.fieldHasError(inps, "litter_effect_notes",  self.Form.LIT_EFF_NOTES_REQ)


class EndpointGroupFunctionality(TestCase):
    def setUp(self):
        build_endpoints_for_permission_testing(self)

    def test_cleaner(self):
        endpoint = Endpoint(animal_group=self.animal_group_working,
                            name='endpoint name',
                            response_units='% affected',
                            data_type='D',
                            NOEL=1,
                            LOEL=-999)
        endpoint.save()

        eg = EndpointGroup(dose_group_id=0,
                           n=20,
                           response=1,
                           variance=1,
                           endpoint=endpoint)

        with self.assertRaises(ValidationError) as err:
            eg.full_clean()

        self.assertItemsEqual(err.exception.messages, [u'Incidence must be numeric'])

        endpoint.data_type = 'C'
        endpoint.save()
        eg = EndpointGroup(dose_group_id=0,
                           n=20,
                           incidence=2,
                           endpoint=endpoint)

        with self.assertRaises(ValidationError) as err:
            eg.full_clean()

        self.assertItemsEqual(err.exception.messages, [u'Variance must be numeric'])

        eg = EndpointGroup(dose_group_id=0,
                           n=20,
                           variance=2,
                           endpoint=endpoint)

        with self.assertRaises(ValidationError) as err:
            eg.full_clean()

        self.assertItemsEqual(err.exception.messages, [u'Response must be numeric'])


class AggregationPermissions(TestCase):
    """
    Ensure endpoint for aggregation views are properly configured.
    """
    def setUp(self):
        build_aggregations_for_permission_testing(self)

    def test_read_success(self):
        clients = ['sudo', 'pm', 'team', 'rev']
        views = [
            reverse('animal:aggregation_list', kwargs={'pk': self.assessment_working.pk}),
            reverse('animal:aggregation_list', kwargs={'pk': self.assessment_final.pk}),
            reverse('animal:aggregation_detail', kwargs={'pk': self.aggregation_working.pk}),
            reverse('animal:aggregation_detail', kwargs={'pk': self.aggregation_final.pk}),
            reverse('animal:aggregation_endpoint_filter', kwargs={'pk': self.assessment_working.pk}),
            reverse('animal:aggregation_endpoint_filter', kwargs={'pk': self.assessment_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))
            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 200)

        clients = ['sudo']
        views = [
            reverse('animal:aggregation_versions', kwargs={'pk': self.aggregation_working.pk}),
            reverse('animal:aggregation_versions', kwargs={'pk': self.aggregation_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))
            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 200)

        clients = ['pm', 'team', 'rev']
        views = [
            reverse('animal:aggregation_versions', kwargs={'pk': self.aggregation_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))
            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 403)

    def test_read_failure(self):
        #anonymous user
        c = Client()
        views = [
            {'view': reverse('animal:aggregation_list', kwargs={'pk': self.assessment_working.pk}), 'status': 403},
            {'view': reverse('animal:aggregation_list', kwargs={'pk': self.assessment_final.pk}), 'status': 200},
            {'view': reverse('animal:aggregation_detail', kwargs={'pk': self.aggregation_working.pk}), 'status': 403},
            {'view': reverse('animal:aggregation_detail', kwargs={'pk': self.aggregation_final.pk}), 'status': 200},
            {'view': reverse('animal:aggregation_versions', kwargs={'pk': self.aggregation_working.pk}), 'status': 403},
            {'view': reverse('animal:aggregation_versions', kwargs={'pk': self.aggregation_final.pk}), 'status': 403},
            {'view': reverse('animal:aggregation_endpoint_filter', kwargs={'pk': self.assessment_working.pk}), 'status': 403},
            {'view': reverse('animal:aggregation_endpoint_filter', kwargs={'pk': self.assessment_final.pk}), 'status': 200},
        ]
        for view in views:
            response = c.get(view['view'])
            self.assertTrue(response.status_code == view['status'])

    def test_crud_success(self):
        # Ensure that sudo, pm and team can create new, edit, and delete
        clients = ['sudo', 'pm', 'team']
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            #create new
            response = c.get(reverse('animal:aggregation_new',
                             kwargs={'pk': self.aggregation_working.pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:aggregation_new',
                              kwargs={'pk': self.aggregation_working.pk}),
                                {"name": 'endpoint name',
                                 "aggregation_type": 'CD',
                                 "endpoints": [self.endpoint_working.pk],
                                 "summary_text": " ",
                                 "dose_units": self.dose_units.pk
                                 })
            self.assertTrue(response.status_code in [200, 302])
            self.assertTemplateUsed('animal/aggregation_detail.html')
            pk = Aggregation.objects.all().latest('created').pk

            #edit
            response = c.get(reverse('animal:aggregation_update',
                             kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:aggregation_update',
                              kwargs={'pk': pk}),
                                {"name": 'new endpoint name',
                                 "aggregation_type": 'CD',
                                 "endpoints": [self.endpoint_working.pk],
                                 "summary_text": " ",
                                 "dose_units": self.dose_units.pk
                                 })
            self.assertTrue(response.status_code in [200, 302])
            self.assertTemplateUsed('animal/aggregation_detail.html')

            #delete
            response = c.get(reverse('animal:aggregation_delete',
                             kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:aggregation_delete', kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('animal/aggregation_assessment_list.html')

    def test_crud_failure(self):
        # make sure that reviewers and those not logged in have any access to
        # these CRUD views on an ongoing assessment
        clients = ['rev', None]
        views = [
            reverse('animal:aggregation_update', kwargs={'pk': self.aggregation_working.pk}),
            reverse('animal:aggregation_new', kwargs={'pk': self.assessment_working.pk}),
            reverse('animal:aggregation_delete', kwargs={'pk': self.aggregation_working.pk}),
            reverse('animal:aggregation_update', kwargs={'pk': self.aggregation_final.pk}),
            reverse('animal:aggregation_new', kwargs={'pk': self.assessment_final.pk}),
            reverse('animal:aggregation_delete', kwargs={'pk': self.aggregation_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 403)
                response = c.post(view)
                self.assertTrue(response.status_code in [403, 405])

        # test that no-one (except sudo) can change a final assessment
        clients = ['pm', 'team', 'rev', None]
        views = [
            reverse('animal:aggregation_update', kwargs={'pk': self.aggregation_final.pk}),
            reverse('animal:aggregation_new', kwargs={'pk': self.assessment_final.pk}),
            reverse('animal:aggregation_delete', kwargs={'pk': self.aggregation_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 403)
                response = c.post(view)
                self.assertTrue(response.status_code in [403, 405])


class UFPermissions(TestCase):
    """
    Ensure permissions for uncertainty factor views are properly configured.
    """
    def setUp(self):
        build_ufs_for_permission_testing(self)

    def test_uf_read_success(self):
        clients = ['sudo', 'pm', 'team', 'rev']
        views = [
            reverse('animal:ufs_list', kwargs={'pk': self.endpoint_working.pk}),
            reverse('animal:ufs_list', kwargs={'pk': self.endpoint_final.pk}),
            reverse('animal:uf_detail', kwargs={'pk': self.ufa_working.pk}),
            reverse('animal:uf_detail', kwargs={'pk': self.ufa_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))
            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 200)

    def test_uf_read_failure(self):
        #anonymous user
        c = Client()
        views = [
            {'view': reverse('animal:uf_detail', kwargs={'pk': self.ufa_final.pk}), 'status': 200},
            {'view': reverse('animal:uf_detail', kwargs={'pk': self.ufa_working.pk}), 'status': 403},
            {'view': reverse('animal:ufs_list', kwargs={'pk': self.endpoint_final.pk}), 'status': 200},
            {'view': reverse('animal:ufs_list', kwargs={'pk': self.endpoint_working.pk}), 'status': 403},
        ]
        for view in views:
            response = c.get(view['view'])
            self.assertTrue(response.status_code == view['status'])

    def test_uf_crud_success(self):
        # Ensure that sudo, pm and team can create new, edit, and delete
        clients = ['sudo', 'pm', 'team']
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            #edit list
            response = c.get(reverse('animal:ufs_list',
                             kwargs={'pk': self.endpoint_working.pk}))
            self.assertTrue(response.status_code == 200)

            #create new
            response = c.get(reverse('animal:uf_create',
                             kwargs={'pk': self.endpoint_working.pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:uf_create',
                              kwargs={'pk': self.endpoint_working.pk}),
                              {'uf_type': 'UFD', 'value': '10', 'description': 'here'})
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('animal/uf_detail.html')
            pk = UncertaintyFactorEndpoint.objects.all().latest('created').pk

            #edit
            response = c.get(reverse('animal:uf_edit',
                             kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:uf_edit',
                              kwargs={'pk': pk}),
                              {'uf_type': 'UFD', 'value': '3', 'description': 'here here'})
            self.assertTrue(response.status_code in [200, 302])
            self.assertTemplateUsed('animal/uf_detail.html')

            #delete
            response = c.get(reverse('animal:uf_delete',
                             kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:uf_delete', kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('animal/endpoint_detail.html')

    def test_uf_crud_failure(self):
        # make sure that reviewers and those not logged in have any access to
        # these CRUD views on an ongoing assessment
        clients = ['rev', None]
        views = [
            reverse('animal:uf_create', kwargs={'pk': self.endpoint_working.pk}),
            reverse('animal:uf_edit', kwargs={'pk': self.ufa_working.pk}),
            reverse('animal:uf_delete', kwargs={'pk': self.ufa_working.pk}),
            reverse('animal:uf_create', kwargs={'pk': self.endpoint_final.pk}),
            reverse('animal:uf_edit', kwargs={'pk': self.ufa_final.pk}),
            reverse('animal:uf_delete', kwargs={'pk': self.ufa_final.pk})
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 403)
                response = c.post(view)
                self.assertTrue(response.status_code in [403, 405])

        # test that no-one (except sudo) can change a final assessment
        clients = ['pm', 'team', 'rev', None]
        views = [
            reverse('animal:uf_create', kwargs={'pk': self.endpoint_final.pk}),
            reverse('animal:uf_edit', kwargs={'pk': self.ufa_final.pk}),
            reverse('animal:uf_delete', kwargs={'pk': self.ufa_final.pk})
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 403)
                response = c.post(view)
                self.assertTrue(response.status_code in [403, 405])


class UFForm(TestCase):
    """
    Test cases for internal form logic.
    """
    def setUp(self):
        build_ufs_for_permission_testing(self)

    def test_uf_value(self):
        c = Client()
        self.assertTrue(c.login(username='team', password='pw'))

        #check to make sure we can create a new UF field
        response = c.post(reverse('animal:uf_create',
                          kwargs={'pk': self.endpoint_working.pk}),
                          {'uf_type': 'UFD', 'value': '10', 'description': 'here'})
        pk = UncertaintyFactorEndpoint.objects.all().latest('created').pk
        self.assertRedirects(response, reverse('animal:uf_detail', kwargs={'pk': pk}))

        #check to make sure we can't create a new UF field that already exists
        response = c.post(reverse('animal:uf_create',
                          kwargs={'pk': self.endpoint_working.pk}),
                          {'uf_type': 'UFA', 'value': '10', 'description': 'here'})
        self.assertFormError(response, 'form', None,
                             ['Error- uncertainty factor type already exists for this endpoint.'])

        #check to make sure we can change an existing UF field to a different type
        response = c.post(reverse('animal:uf_edit',
                          kwargs={'pk': self.ufa_working.pk}),
                          {'uf_type': 'UFB', 'value': '10', 'description': 'here'})
        self.assertTrue(response.status_code == 200)
        self.assertTemplateUsed('animal/uf_detail.html')

        #check to make sure we can change an existing UF field to a same UF type
        response = c.post(reverse('animal:uf_edit',
                          kwargs={'pk': self.ufa_working.pk}),
                          {'uf_type': 'UFA', 'value': '5', 'description': 'here'})
        self.assertTrue(response.status_code in [200, 302])
        self.assertTemplateUsed('animal/uf_detail.html')
