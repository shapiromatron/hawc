from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from celery.task.control import inspect
from selenium import webdriver

from . import utils


class CeleryTests(TestCase):
    def test_isRunning(self):
        insp = inspect()
        d = insp.stats()
        self.assertTrue(d is not None)


class MainPageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ff = webdriver.Firefox()

    def test_isRunning(self):
        self.ff.get("http://localhost:8000")
        assert "Health Assessment Workspace Collaborative" in self.ff.title

    @classmethod
    def tearDownClass(cls):
        cls.ff.quit()


class PermissionTests(TestCase):
    """
    Ensure permissions for assessment-level views are properly configured.
    """

    def setUp(self):
        utils.build_assessments_for_permissions_testing(self)

    def tearDown(self):
        self.superuser.delete()
        self.project_manager.delete()
        self.team_member.delete()
        self.reviewer.delete()
        try:  # may be deleted in test
            self.assessment_working.delete()
            self.assessment_final.delete()
        except Exception:
            pass

    # new-level permissions
    def test_new_success(self):
        clients = ("sudo@sudo.com", "pm@pm.com", "team@team.com", "rev@rev.com")
        views = ("assessment:new",)
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password="pw"))
            for view in views:
                response = c.get(reverse(view))
                self.assertTrue(response.status_code == 200)
                response = c.post(
                    reverse(view),
                    {
                        "name": "testing",
                        "year": "2013",
                        "version": "1",
                        "public": "off",
                        "editable": "on",
                        "project_manager": ("1"),
                        "team_members": ("1", "2"),
                        "reviewers": ("1"),
                    },
                )
                self.assertTemplateUsed("assessment/assessment_detail.html")
                self.assertTrue(response.status_code in [200, 302])

    def test_new_forbidden(self):
        clients = (None,)
        views = ("assessment:new",)
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(email=client, password="pw"))
            for view in views:
                c.get(reverse(view))
                self.assertTemplateUsed("registration/login.html")
                c.post(
                    reverse(view),
                    {
                        "name": "testing",
                        "year": "2013",
                        "version": "1",
                        "public": "off",
                        "editable": "on",
                        "project_manager": ("1"),
                        "team_members": ("1", "2"),
                        "reviewers": ("1"),
                    },
                )
                self.assertTemplateUsed("registration/login.html")

    # Detail view permissions
    def test_detail_success(self):
        clients = ("sudo@sudo.com", "pm@pm.com", "team@team.com", "rev@rev.com")
        views = ("assessment:detail",)
        pks = (self.assessment_working.pk, self.assessment_final.pk)
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(email=client, password="pw"))
            for view in views:
                for pk in pks:
                    response = c.get(reverse(view, kwargs={"pk": pk}))
                    self.assertTrue(response.status_code == 200)

    def test_detail_view_public(self):
        c = Client()
        response = c.get(reverse("assessment:detail", kwargs={"pk": self.assessment_working.pk}))
        self.assertTrue(response.status_code == 403)
        response = c.get(reverse("assessment:detail", kwargs={"pk": self.assessment_final.pk}))
        self.assertTrue(response.status_code == 200)

    # Edit view permissions
    def test_edit_view_success(self):
        clients = ("sudo@sudo.com", "pm@pm.com")
        views = ("assessment:update", "assessment:delete")
        pks = (self.assessment_working.pk, self.assessment_final.pk)
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(email=client, password="pw"))
            for view in views:
                for pk in pks:
                    response = c.get(reverse(view, kwargs={"pk": pk}))
                    self.assertTrue(response.status_code == 200)

            # check post updates
            response = c.post(
                reverse("assessment:update", kwargs={"pk": self.assessment_working.pk}),
                {"name": "foo manchu"},
            )
            self.assertTemplateUsed("assessment/assessment_detail.html")
            self.assertTrue(response.status_code == 200)
            response = c.post(
                reverse("assessment:update", kwargs={"pk": self.assessment_final.pk}),
                {"name": "foo manchu"},
            )
            self.assertTemplateUsed("assessment/assessment_detail.html")
            self.assertTrue(response.status_code == 200)

    def test_edit_view_forbidden(self):
        clients = (None, "team@team.com", "rev@rev.com")
        views = ("assessment:update", "assessment:delete")
        pks = [self.assessment_working.pk, self.assessment_final.pk]
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(email=client, password="pw"))
            for pk in pks:
                for view in views:
                    response = c.get(reverse(view, kwargs={"pk": pk}))
                    self.assertTrue(response.status_code == 403)

                # check POST
                response = c.post(
                    reverse("assessment:update", kwargs={"pk": pk}), {"name": "foo manchu"},
                )
                self.assertTrue(response.status_code == 403)

    # POST Delete permissions
    def test_delete_superuser(self):
        c = Client()
        self.assertTrue(c.login(email="sudo@sudo.com", password="pw"))
        response = c.post(reverse("assessment:delete", kwargs={"pk": self.assessment_working.pk}))
        self.assertTrue(response.status_code == 302)
        self.assertTemplateUsed("assessment/assessment_list.html")
        response = c.post(reverse("assessment:delete", kwargs={"pk": self.assessment_final.pk}))
        self.assertTrue(response.status_code == 302)
        self.assertTemplateUsed("assessment/assessment_list.html")

    def test_delete_project_manager(self):
        c = Client()
        self.assertTrue(c.login(email="pm@pm.com", password="pw"))
        response = c.post(reverse("assessment:delete", kwargs={"pk": self.assessment_working.pk}))
        self.assertTrue(response.status_code == 302)
        self.assertTemplateUsed("assessment/assessment_list.html")

        response = c.post(reverse("assessment:delete", kwargs={"pk": self.assessment_final.pk}))
        self.assertTrue(response.status_code == 302)
        self.assertTemplateUsed("assessment/assessment_list.html")

    def test_delete_forbidden(self):
        clients = (None, "team@team.com", "rev@rev.com")
        pks = (self.assessment_working.pk, self.assessment_final.pk)
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(email=client, password="pw"))
            for pk in pks:
                response = c.post(reverse("assessment:delete", kwargs={"pk": pk}))
                self.assertTrue(response.status_code == 403)
