import re

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from .utils import build_studies_for_permission_testing


class StudyPermissions(TestCase):
    """
    Ensure permissions for study-level views are properly configured.
    """

    def setUp(self):
        build_studies_for_permission_testing(self)

    def test_study_read_success(self):
        clients = ["sudo@sudo.com", "pm@pm.com", "team@team.com", "rev@rev.com"]
        views = [
            reverse("study:list", kwargs={"pk": self.assessment_working.pk}),
            reverse("study:detail", kwargs={"pk": self.study_working.pk}),
            reverse("study:list", kwargs={"pk": self.assessment_final.pk}),
            reverse("study:detail", kwargs={"pk": self.study_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password="pw"))
            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 200)

    def test_study_read_failure(self):
        # anonymous user
        c = Client()
        views = [
            {
                "view": reverse("study:list", kwargs={"pk": self.assessment_working.pk}),
                "status": 403,
            },
            {"view": reverse("study:detail", kwargs={"pk": self.study_working.pk}), "status": 403},
            {
                "view": reverse("study:list", kwargs={"pk": self.assessment_final.pk}),
                "status": 200,
            },
            {"view": reverse("study:detail", kwargs={"pk": self.study_final.pk}), "status": 200},
        ]
        for view in views:
            response = c.get(view["view"])
            self.assertTrue(response.status_code == view["status"])

    def test_study_crud_success(self):
        # Check to ensure that sudo, pm and team have CRUD permissions.
        # Create a new study, edit, view prior versions, and delete. Test both
        # GET and POST when appropriate.
        clients = ["sudo@sudo.com", "pm@pm.com", "team@team.com"]
        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password="pw"))

            # create new
            response = c.get(reverse("study:new_ref", kwargs={"pk": self.assessment_working.pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(
                reverse("study:new_ref", kwargs={"pk": self.assessment_working.pk}),
                {
                    "assessment": self.assessment_working.pk,
                    "short_citation": "foo et al.",
                    "full_citation": "cite",
                    "bioassay": True,
                    "coi_reported": 0,
                },
            )
            self.assertTrue(response.status_code == 302)
            self.assertTemplateUsed("study/study_detail.html")
            pk = int(re.findall(r"/study/(\d+)/$", response["location"])[0])

            # edit
            response = c.get(reverse("study:update", kwargs={"pk": pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(
                reverse("study:update", kwargs={"pk": pk}),
                {
                    "assessment": self.assessment_working.pk,
                    "citation": "foo et al.",
                    "full_citation": "cite",
                },
            )
            self.assertTrue(response.status_code in [200, 302])
            self.assertTemplateUsed("study/study_detail.html")

            # view versions
            response = c.get(reverse("study:update", kwargs={"pk": pk}))
            self.assertTrue(response.status_code == 200)

            # delete
            response = c.get(reverse("study:delete", kwargs={"pk": pk}))
            self.assertTrue(response.status_code == 200)
            response = c.post(reverse("study:delete", kwargs={"pk": pk}))
            self.assertTrue(response.status_code == 302)

    def test_uf_crud_failure(self):
        # Check to ensure that rev and None don't have CRUD permissions.
        # Attempt to create a new study, edit, view prior versions, and delete.
        # Test both GET and POST when appropriate.

        # first test working scenario
        clients = ["rev@rev.com", None]
        views = [
            reverse("study:new_ref", kwargs={"pk": self.assessment_working.pk}),
            reverse("study:update", kwargs={"pk": self.study_working.pk}),
            reverse("study:delete", kwargs={"pk": self.study_working.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password="pw"))

            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 403)
                response = c.post(view)
                self.assertTrue(response.status_code in [403, 405])

        # next check that all people (except sudo) cannot edit a final study
        clients = ["pm@pm.com", "team@team.com", "rev@rev.com", None]
        views = [
            reverse("study:new_ref", kwargs={"pk": self.assessment_final.pk}),
            reverse("study:update", kwargs={"pk": self.study_final.pk}),
            reverse("study:delete", kwargs={"pk": self.study_final.pk}),
        ]

        for client in clients:
            c = Client()
            if client:
                self.assertTrue(c.login(username=client, password="pw"))

            for view in views:
                response = c.get(view)
                self.assertTrue(response.status_code == 403)
                response = c.post(view)
                self.assertTrue(response.status_code in [403, 405])
