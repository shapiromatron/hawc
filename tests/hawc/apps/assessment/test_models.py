import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.test.client import RequestFactory

from hawc.apps.assessment import constants, models


@pytest.mark.django_db
class TestJob:
    def test_job_success(self, db_keys):
        job = models.Job.objects.create(job=constants.JobType.TEST)
        ran_job = models.Job.objects.get(pk=job.task_id)

        assert ran_job.status == constants.JobStatus.SUCCESS
        assert ran_job.result.get("data") == "SUCCESS"

    def test_job_failure(self, db_keys):
        job = models.Job.objects.create(job=constants.JobType.TEST, kwargs={"fail": True})
        ran_job = models.Job.objects.get(pk=job.task_id)

        assert ran_job.status == constants.JobStatus.FAILURE
        assert ran_job.result.get("error") == "FAILURE"


class TestContent:
    @pytest.mark.django_db
    def test_rendered_page(self):
        rf = RequestFactory()
        request = rf.get("/")
        request.user = AnonymousUser()
        page = models.Content.rendered_page(models.ContentTypeChoices.HOMEPAGE, request, {})
        assert "<h1>Welcome to HAWC</h1>" in page
        page = models.Content.rendered_page(models.ContentTypeChoices.ABOUT, request, {})
        assert page == "<h1>About HAWC</h1>"

    @pytest.mark.django_db
    def test_cache_lifecycle(self):
        rf = RequestFactory()
        request = rf.get("/")
        request.user = AnonymousUser()
        page = models.Content.objects.get(content_type=models.ContentTypeChoices.HOMEPAGE)
        page.template = "<h1>Hello {{name}}!</h1>"
        page.save()
        key = page.get_cache_key(page.content_type)
        assert cache.get(key) is None
        html = models.Content.rendered_page(
            models.ContentTypeChoices.HOMEPAGE, request, {"name": "Thor"}
        )
        assert html == "<h1>Hello Thor!</h1>"
        assert cache.get(key) == "<h1>Hello Thor!</h1>"
        page.clear_cache()
        assert cache.get(key) is None


class TestAssessmentDetail:
    def test_get_peer_review_status_display(self):
        obj = models.AssessmentDetail(peer_review_status=constants.PeerReviewType.JOURNAL)
        assert obj.get_peer_review_status_display() == constants.PeerReviewType.JOURNAL.label

        obj = models.AssessmentDetail(peer_review_status=constants.PeerReviewType.OTHER)
        assert obj.get_peer_review_status_display() == ""
