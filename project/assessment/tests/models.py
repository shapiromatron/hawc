from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from . import utils


class AssessmentTests(TestCase):
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
        except:
            pass

    def test_two_assessment_name(self):
        # test two assessments with duplicate information can be created.
        c = Client()
        self.assertTrue(c.login(email="sudo@sudo.com", password="pw"))
        for i in range(2):
            response = c.post(
                reverse("assessment:new"),
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
