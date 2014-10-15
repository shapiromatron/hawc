import re

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from study.models import Study
from assessment.tests import build_assessments_for_permissions_testing


def build_studies_for_permission_testing(obj):
    build_assessments_for_permissions_testing(obj)

    obj.study_working = Study(assessment=obj.assessment_working,
                              study_type=0,
                              full_citation="Foo et al.",
                              short_citation="Foo et al.")
    obj.study_working.save()

    obj.study_final = Study(assessment=obj.assessment_final,
                            study_type=0,
                            full_citation="Foo et al.",
                            short_citation="Foo et al.")
    obj.study_final.save()


class StudyPermissions(TestCase):
    """
    Ensure permissions for study-level views are properly configured.
    """
    def setUp(self):
        build_studies_for_permission_testing(self)

    def test_study_read_success(self):
        clients = ['sudo', 'pm', 'team', 'rev']
        views = [
            reverse('study:list', kwargs={'pk': self.assessment_working.pk}),
            reverse('study:detail', kwargs={'pk': self.study_working.pk}),
            # reverse('study:endpoint_table', kwargs={'pk': self.study_working.pk}),
            reverse('study:list', kwargs={'pk': self.assessment_final.pk}),
            reverse('study:detail', kwargs={'pk': self.study_final.pk}),
            # reverse('study:endpoint_table', kwargs={'pk': self.study_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))
            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 200)

    def test_study_read_failure(self):
        #anonymous user
        c = Client()
        views = [
            {'view': reverse('study:list', kwargs={'pk': self.assessment_working.pk}), 'status': 403},
            {'view': reverse('study:detail', kwargs={'pk': self.study_working.pk}), 'status': 403},
            # {'view': reverse('study:endpoint_table', kwargs={'pk': self.study_working.pk}), 'status': 403},
            {'view': reverse('study:list', kwargs={'pk': self.assessment_final.pk}), 'status': 200},
            {'view': reverse('study:detail', kwargs={'pk': self.study_final.pk}), 'status': 200},
            # {'view': reverse('study:endpoint_table', kwargs={'pk': self.study_final.pk}), 'status': 200},
        ]
        for view in views:
            response = c.get(view['view'])
            self.assertTrue(response.status_code == view['status'])

    def test_study_crud_sucess(self):
        # Check to ensure that sudo, pm and team have CRUD permissions.
        # Create a new study, edit, view prior versions, and delete. Test both
        # GET and POST when appropriate.
        clients = ['sudo', 'pm', 'team']
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))

            #create new
            response = c.get(reverse('study:new_study', kwargs={'pk': self.assessment_working.pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('study:new_study', kwargs={'pk': self.assessment_working.pk}),
                              {'assessment': self.assessment_working.pk,
                               'citation': 'foo et al.', 'full_citation': 'cite', 'summary': 'summary here.'})
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed('study/study_detail.html')
            pk = re.findall(r'/study/(\d+)/$', response['location'])
            pk = int(pk[0])

            #edit
            response = c.get(reverse('study:update', kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('study:update', kwargs={'pk': pk}),
                              {'assessment': self.assessment_working.pk,
                               'citation': 'foo et al.', 'full_citation': 'cite', 'summary': 'summary there.'})
            self.assertTrue(response.status_code in [200, 302])
            self.assertTemplateUsed('study/study_detail.html')

            #view versions
            response = c.get(reverse('study:update', kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)

            #delete
            response = c.get(reverse('study:delete', kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('study:delete', kwargs={'pk': pk}))
            self.assertTrue(response.status_code == 302)

    def test_uf_crud_failure(self):
        # Check to ensure that rev and None don't have CRUD permissions.
        # Attempt to create a new study, edit, view prior versions, and delete.
        # Test both GET and POST when appropriate.

        #first test working scenario
        clients = ['rev', None]
        views = [
            reverse('study:new_study', kwargs={'pk': self.assessment_working.pk}),
            reverse('study:update', kwargs={'pk': self.study_working.pk}),
            reverse('study:delete', kwargs={'pk': self.study_working.pk}),
            reverse('study:versions', kwargs={'pk': self.study_working.pk}),
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

        # next check that all people (except sudo) can edit a finalized assessment
        clients = ['pm', 'team', 'rev', None]
        views = [
            reverse('study:new_study', kwargs={'pk': self.assessment_final.pk}),
            reverse('study:update', kwargs={'pk': self.study_final.pk}),
            reverse('study:delete', kwargs={'pk': self.study_final.pk}),
            reverse('study:versions', kwargs={'pk': self.study_final.pk}),
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


class StudyFormTests(TestCase):
    """
    Test cases for internal form logic.
    """
    def setUp(self):
        build_studies_for_permission_testing(self)

    def test_uf_value(self):
        c = Client()
        self.assertTrue(c.login(username='team', password='pw'))

        study_dict = {'full_citation': 'foo et al.',
                      'short_citation': 'foo_citation',
                      'summary': 'summary there.'}

        #check to make sure we can create a new study field
        response = c.post(reverse('study:new_study', kwargs={'pk': self.assessment_working.pk}),
            study_dict)
        pk = re.findall(r'/study/(\d+)/$', response['location'])
        pk = int(pk[0])
        self.assertRedirects(response, reverse('study:detail', kwargs={'pk': pk}))

        #check to make sure we can't create a new study citation field that already exists
        response = c.post(reverse('study:new_study', kwargs={'pk': self.assessment_working.pk}),
            study_dict)
        self.assertFormError(response, 'form', None, u'Error- short-citation name must be unique for assessment.')

        #check to make sure we can change an existing study citation field to a different type
        response = c.post(reverse('study:update', kwargs={'pk': pk}),
            study_dict)
        self.assertTrue(response.status_code in [200, 302])
        self.assertTemplateUsed('study/study_detail.html')

        #check to make sure we can create a new study in different assessment
        c.logout()
        self.assertTrue(c.login(username='sudo', password='pw'))

        response = c.post(reverse('study:new_study', kwargs={'pk': self.assessment_final.pk}),
            study_dict)
        pk = re.findall(r'/study/(\d+)/$', response['location'])
        pk = int(pk[0])
        self.assertRedirects(response, reverse('study:detail', kwargs={'pk': pk}))
