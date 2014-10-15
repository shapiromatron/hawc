from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from celery.task.control import inspect

from myuser.models import HAWCUser

from .models import Assessment

from django.core.management import call_command

class CeleryTests(TestCase):

    def test_isRunning(self):
        insp = inspect()
        d = insp.stats()
        self.assertTrue(d != None)


def build_assessments_for_permissions_testing(obj):
    # builds assessments to be used for tests; note that other test-suites may
    # call this function as well

    try:
        call_command('createcachetable', 'dev_cache_table', interactive=False)
    except:
        pass

    obj.superuser = HAWCUser.objects.create_superuser('sudo@sudo.com', 'pw')
    obj.project_manager = HAWCUser.objects.create_user('pm@pm.com', 'pw')
    obj.team_member = HAWCUser.objects.create_user('team@team.com', 'pw')
    obj.reviewer = HAWCUser.objects.create_user('rev@rev.com', 'pw')

    # setup default working assessment
    obj.assessment_working = Assessment(name='working',
                                        year=1999,
                                        version='1.0',
                                        editable=True,
                                        public=False)
    obj.assessment_working.save()
    obj.assessment_working.project_manager.add(obj.project_manager)
    obj.assessment_working.team_members.add(obj.team_member)
    obj.assessment_working.reviewers.add(obj.reviewer)

    # setup default fixed assessment
    obj.assessment_final = Assessment(name='final',
                                      year=2001,
                                      version='final',
                                      editable=False,
                                      public=True)
    obj.assessment_final.save()
    obj.assessment_final.project_manager.add(obj.project_manager)
    obj.assessment_final.team_members.add(obj.team_member)
    obj.assessment_final.reviewers.add(obj.reviewer)


class PermissionTests(TestCase):
    """
    Ensure permissions for assessment-level views are properly configured.
    """
    def setUp(self):
        build_assessments_for_permissions_testing(self)

    def tearDown(self):
        self.superuser.delete()
        self.project_manager.delete()
        self.team_member.delete()
        self.reviewer.delete()
        try:  # may be deleted in test
            self.assessment_working.delete()
            self.assessment_final.delete()
        except:
            pass

    # new-level permissions
    def test_new_success(self):
        clients = ('sudo@sudo.com', 'pm@pm.com', 'team@team.com', 'rev@rev.com')
        views = ('assessment:new', )
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password='pw'))
            for view in views:
                response = c.get(reverse(view))
                self.assertTrue(response.status_code == 200)
                response = c.post(reverse(view), {'name': 'testing',
                                                  'year': '2013',
                                                  'version': '1',
                                                  'public': 'off',
                                                  'editable': 'on',
                                                  'project_manager': ('1'),
                                                  'team_members': ('1', '2'),
                                                  'reviewers': ('1')})
                self.assertTemplateUsed('assessment/assessment_detail.html')
                self.assertTrue(response.status_code in [200, 302])

    def test_new_forbidden(self):
        clients = (None, )
        views = ('assessment:new', )
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(email=client, password='pw'))
            for view in views:
                c.get(reverse(view))
                self.assertTemplateUsed('registration/login.html')
                c.post(reverse(view), {'name': 'testing',
                                       'year': '2013',
                                       'version': '1',
                                       'public': 'off',
                                       'editable': 'on',
                                       'project_manager': ('1'),
                                       'team_members': ('1', '2'),
                                       'reviewers': ('1')})
                self.assertTemplateUsed('registration/login.html')

    # Detail view permissions
    def test_detail_success(self):
        clients = ('sudo@sudo.com', 'pm@pm.com', 'team@team.com', 'rev@rev.com')
        views = ('assessment:detail', )
        pks = (self.assessment_working.pk, self.assessment_final.pk)
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(email=client, password='pw'))
            for view in views:
                for pk in pks:
                    response = c.get(reverse(view, kwargs={'pk': pk}))
                    self.assertTrue(response.status_code == 200)

    def test_detail_view_public(self):
        c = Client()
        response = c.get(reverse('assessment:detail', kwargs={'pk': self.assessment_working.pk}))
        self.assertTrue(response.status_code == 403)
        response = c.get(reverse('assessment:detail', kwargs={'pk': self.assessment_final.pk}))
        self.assertTrue(response.status_code == 200)

    # Edit view permissions
    def test_edit_view_success(self):
        clients = ('sudo@sudo.com', 'pm@pm.com')
        views = ('assessment:update', 'assessment:versions', 'assessment:delete')
        pks = (self.assessment_working.pk, self.assessment_final.pk)
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(email=client, password='pw'))
            for view in views:
                for pk in pks:
                    response = c.get(reverse(view, kwargs={'pk': pk}))
                    self.assertTrue(response.status_code == 200)

            # check post updates
            response = c.post(reverse('assessment:update',
                              kwargs={'pk': self.assessment_working.pk}),
                              {'name': 'foo manchu'})
            self.assertTemplateUsed('assessment/assessment_detail.html')
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse('assessment:update',
                              kwargs={'pk': self.assessment_final.pk}),
                              {'name': 'foo manchu'})
            self.assertTemplateUsed('assessment/assessment_detail.html')
            self.assertTrue(response.status_code == 200)

    def test_edit_view_forbidden(self):
        clients = (None, 'team@team.com', 'rev@rev.com')
        views = ('assessment:update', 'assessment:versions', 'assessment:delete')
        pks = [self.assessment_working.pk, self.assessment_final.pk]
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(email=client, password='pw'))
            for pk in pks:
                for view in views:
                    response = c.get(reverse(view, kwargs={'pk': pk}))
                    self.assertTrue(response.status_code == 403)

                # check POST
                response = c.post(reverse('assessment:update', kwargs={'pk': pk}),
                                  {'name': 'foo manchu'})
                self.assertTrue(response.status_code == 403)

    # POST Delete permissions
    def test_delete_superuser(self):
        c = Client()
        self.assertTrue(c.login(email='sudo@sudo.com', password='pw'))
        response = c.post(reverse('assessment:delete', kwargs={'pk': self.assessment_working.pk}))
        self.assertTrue(response.status_code == 302)
        self.assertTemplateUsed('assessment/assessment_list.html')
        response = c.post(reverse('assessment:delete', kwargs={'pk': self.assessment_final.pk}))
        self.assertTrue(response.status_code == 302)
        self.assertTemplateUsed('assessment/assessment_list.html')

    def test_delete_project_manager(self):
        c = Client()
        self.assertTrue(c.login(email='pm@pm.com', password='pw'))
        response = c.post(reverse('assessment:delete', kwargs={'pk': self.assessment_working.pk}))
        self.assertTrue(response.status_code == 302)
        self.assertTemplateUsed('assessment/assessment_list.html')
        response = c.post(reverse('assessment:delete', kwargs={'pk': self.assessment_final.pk}))
        self.assertTrue(response.status_code == 302)
        self.assertTemplateUsed('assessment/assessment_list.html')

    def test_delete_forbidden(self):
        clients = (None, 'team@team.com', 'rev@rev.com')
        pks = (self.assessment_working.pk, self.assessment_final.pk)
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(email=client, password='pw'))
            for pk in pks:
                response = c.post(reverse('assessment:delete', kwargs={'pk': pk}))
                self.assertTrue(response.status_code == 403)


class AssessmentTests(TestCase):

    def setUp(self):
        build_assessments_for_permissions_testing(self)

    def tearDown(self):
        self.superuser.delete()
        self.project_manager.delete()
        self.team_member.delete()
        self.reviewer.delete()
        try:  # may be deleted in test
            self.assessment_working.delete()
            self.assessment_final.delete()
        except:
            pass

    def test_two_assessment_name(self):
        # test two assessments with duplicate information can be created.
        c = Client()
        self.assertTrue(c.login(email='sudo@sudo.com', password='pw'))
        for i in xrange(2):
            response = c.post(reverse('assessment:new'), {'name': 'testing',
                                                          'year': '2013',
                                                          'version': '1',
                                                          'public': 'off',
                                                          'editable': 'on',
                                                          'project_manager': ('1'),
                                                          'team_members': ('1', '2'),
                                                          'reviewers': ('1')})
            self.assertTemplateUsed('assessment/assessment_detail.html')
            self.assertTrue(response.status_code in [200, 302])
