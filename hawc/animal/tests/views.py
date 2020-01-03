from unittest import skip

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from animal import models

from . import utils


class ExperimentPermissions(TestCase):
    """
    Ensure permissions for experiment views are properly configured.
    """
    def setUp(self):
        utils.build_experiments_for_permission_testing(self)

    def test_read_success(self):
        clients = ['sudo@sudo.com', 'pm@pm.com', 'team@team.com', 'rev@rev.com']
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
        # anonymous user
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
        clients = ['sudo@sudo.com', 'pm@pm.com', 'team@team.com']
        exp_post = {'name': 'experiment name', 'type': 'Ac', 'description': 'No description.' }
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            # create new
            response = c.get(reverse('animal:experiment_new', kwargs={'pk': self.study_working.pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(
                reverse('animal:experiment_new', kwargs={'pk': self.study_working.pk}),
                exp_post)
            self.assertTemplateUsed('animal/experiment_detail.html')
            pk = models.Experiment.objects.all().latest('created').pk

            # edit
            response = c.get(reverse('animal:experiment_update', kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(
                reverse('animal:experiment_update', kwargs={'pk': pk}),
                exp_post)
            self.assertTemplateUsed('animal/experiment_detail.html')

            # delete
            response = c.get(reverse('animal:experiment_delete', kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(
                reverse('animal:experiment_delete', kwargs={'pk': pk}))
            self.assertTemplateUsed('study/study_detail.html')

    def test_crud_failure(self):
        # make sure that reviewers and those not logged in have any access to
        # these CRUD views on an ongoing assessment
        clients = ['rev@rev.com', None]
        views = [
            reverse('animal:experiment_update', kwargs={'pk': self.experiment_working.pk}),
            reverse('animal:experiment_new', kwargs={'pk': self.study_working.pk}),
            reverse('animal:experiment_delete', kwargs={'pk': self.experiment_working.pk}),
            reverse('animal:experiment_update', kwargs={'pk': self.experiment_final.pk}),
            reverse('animal:experiment_new', kwargs={'pk': self.study_final.pk}),
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
        clients = ['pm@pm.com', 'team@team.com', 'rev@rev.com', None]
        views = [
            reverse('animal:experiment_update', kwargs={'pk': self.experiment_final.pk}),
            reverse('animal:experiment_new', kwargs={'pk': self.study_final.pk}),
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


class AnimalGroupPermissions(TestCase):
    """
    Ensure permissions for animal-group views are properly configured.
    """
    def setUp(self):
        utils.build_animal_groups_for_permission_testing(self)

    def test_read_success(self):
        clients = ['sudo@sudo.com', 'pm@pm.com', 'team@team.com', 'rev@rev.com']
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
        # anonymous user
        c = Client()
        views = [
            {'view': reverse('animal:animal_group_detail', kwargs={'pk': self.animal_group_final.pk}), 'status': 200},
            {'view': reverse('animal:animal_group_detail', kwargs={'pk': self.animal_group_working.pk}), 'status': 403},
        ]
        for view in views:
            response = c.get(view['view'])
            self.assertTrue(response.status_code == view['status'])

    @skip("TODO: fix animal-group creation")
    def test_crud_success(self):
        # check to ensure that sudo, pm and team can view the edit list,
        # create a new animal_group, edit it, and delete it
        clients = ['sudo@sudo.com', 'pm@pm.com', 'team@team.com']
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            # create new
            response = c.get(reverse('animal:animal_group_new',
                             kwargs={'pk': self.experiment_working.pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(
                reverse('animal:animal_group_new', kwargs={'pk': self.experiment_working.pk}),
                {
                    "experiment": self.experiment_working.pk,
                    "name": 'animal group name',
                    "species": self.species.pk,
                    "strain": self.strain.pk,
                    "sex": 'M',
                    "dose_groups": 4
                })
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('animal/animal_group_detail.html')
            pk = models.AnimalGroup.objects.all().latest('created').pk

            # edit
            response = c.get(reverse('animal:animal_group_update',
                             kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:animal_group_update',
                              kwargs={'pk': pk}),
                              {"experiment": self.experiment_working.pk,
                               "name": 'animal group name',
                               "species": self.species.pk,
                               "strain": self.strain.pk,
                               "sex": 'M'})
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('animal/animal_group_detail.html')

            # delete
            response = c.get(reverse('animal:animal_group_delete',
                             kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:animal_group_delete', kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('animal/experiment_detail.html')

    def test_crud_failure(self):
        # make sure that reviewers and those not logged in have any access to
        # these CRUD views on an ongoing assessment
        clients = ['rev@rev.com', None]
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
        clients = ['pm@pm.com', 'team@team.com', 'rev@rev.com', None]
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
                self.assertTrue(response.status_code == 403)


class EndpointPermissions(TestCase):
    """
    Ensure endpoint for animal-group views are properly configured.
    """
    def setUp(self):
        utils.build_endpoints_for_permission_testing(self)

    def test_read_success(self):
        clients = ['sudo@sudo.com', 'pm@pm.com', 'team@team.com', 'rev@rev.com']
        views = [
            reverse('animal:endpoint_list', kwargs={'pk': self.assessment_working.pk}),
            reverse('animal:endpoint_list', kwargs={'pk': self.assessment_final.pk}),
            reverse('animal:assessment_endpoint_taglist', kwargs={'pk': self.assessment_working.pk, 'tag_slug': 'foo'}),
            reverse('animal:assessment_endpoint_taglist', kwargs={'pk': self.assessment_final.pk, 'tag_slug': 'foo'}),
            reverse('animal:endpoint_detail', kwargs={'pk': self.endpoint_working.pk}),
            reverse('animal:endpoint_detail', kwargs={'pk': self.endpoint_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))
            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 200)

    def test_read_failure(self):
        # anonymous user
        c = Client()
        views = [
            {'view': reverse('animal:endpoint_list', kwargs={'pk': self.assessment_working.pk}), 'status': 403},
            {'view': reverse('animal:endpoint_list', kwargs={'pk': self.assessment_final.pk}), 'status': 200},
            {'view': reverse('animal:assessment_endpoint_taglist', kwargs={'pk': self.assessment_working.pk, 'tag_slug': 'foo'}), 'status': 403},
            {'view': reverse('animal:assessment_endpoint_taglist', kwargs={'pk': self.assessment_final.pk, 'tag_slug': 'foo'}), 'status': 200},
            {'view': reverse('animal:endpoint_detail', kwargs={'pk': self.endpoint_working.pk}), 'status': 403},
            {'view': reverse('animal:endpoint_detail', kwargs={'pk': self.endpoint_final.pk}), 'status': 200},
        ]
        for view in views:
            response = c.get(view['view'])
            self.assertTrue(response.status_code == view['status'])

    @skip("TODO: fix endpoint creation")
    def test_crud_success(self):
        # check to ensure that sudo, pm and team can view the edit list,
        # create a new endpoint, edit it, and delete it
        clients = ['sudo@sudo.com', 'pm@pm.com', 'team@team.com']
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            # create new
            response = c.get(reverse('animal:endpoint_new', kwargs={'pk': self.animal_group_working.pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(
                reverse('animal:endpoint_new', kwargs={'pk': self.animal_group_working.pk}),
                {
                    "animal_group": self.animal_group_working.pk,
                    "name": 'endpoint name',
                    "response_units": '% affected',
                    "data_type": 'D',
                    "NOEL": 1,
                    "LOEL": -999,
                    "egs_json": '[{"dose_group_id":0,"n":20,"incidence":1,"response":null,"variance":null},{"dose_group_id":1,"n":20,"incidence":2,"response":null,"variance":null},{"dose_group_id":2,"n":20,"incidence":3,"response":null,"variance":null},{"dose_group_id":3,"n":20,"incidence":4,"response":null,"variance":null}]'
                })
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('animal/endpoint_detail.html')
            pk = models.Endpoint.objects.all().latest('created').pk

            # edit
            response = c.get(reverse('animal:endpoint_update', kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(
                reverse('animal:endpoint_update', kwargs={'pk': pk}),
                {
                    "animal_group": self.animal_group_working.pk,
                    "name": 'endpoint name',
                    "response_units": '% affected',
                    "data_type": 'D',
                    "NOEL": 1,
                    "LOEL": -999,
                    "egs_json": '[{"dose_group_id":0,"n":20,"incidence":1,"response":null,"variance":null},{"dose_group_id":1,"n":20,"incidence":2,"response":null,"variance":null},{"dose_group_id":2,"n":20,"incidence":3,"response":null,"variance":null},{"dose_group_id":3,"n":20,"incidence":4,"response":null,"variance":null}]'
                })
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('animal/endpoint_detail.html')

            # delete
            response = c.get(reverse('animal:endpoint_delete', kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('animal:endpoint_delete', kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('animal/animal_group_detail.html')

    def test_crud_failure(self):
        # make sure that reviewers and those not logged in have any access to
        # these CRUD views on an ongoing assessment
        clients = ['rev@rev.com', None]
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
        clients = ['pm@pm.com', 'team@team.com', 'rev@rev.com', None]
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
