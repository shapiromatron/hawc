import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.assessment import models


@pytest.mark.django_db
def test_assessment_creation():
    c = Client()
    assert c.login(email="sudo@sudo.com", password="pw") is True
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
        assertTemplateUsed("assessment/assessment_detail.html")
        assert response.status_code in [200, 302]


@pytest.mark.django_db
class TestJob:
    def test_job_success(self, db_keys):
        job = models.Job.objects.create(job=models.Job.TEST)
        ran_job = models.Job.objects.get(pk=job.task_id)

        assert ran_job.status == models.Job.SUCCESS
        assert ran_job.result == "SUCCESS"

    def test_job_failure(self, db_keys):
        job = models.Job.objects.create(job=models.Job.TEST, kwargs={"fail": True})
        ran_job = models.Job.objects.get(pk=job.task_id)

        assert ran_job.status == models.Job.FAILURE
        assert ran_job.exception == "FAILURE"
