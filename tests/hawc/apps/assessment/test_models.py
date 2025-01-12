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


@pytest.mark.django_db
class TestLabel:
    def test_get_labelled_items_url(self):
        assessment = models.Assessment.objects.get(id=1)
        root = models.Label.get_assessment_root(assessment.id)
        root.add_child(name="test", published=False, assessment=assessment)
        assert "/labeled-items/" in root.get_labelled_items_url()

    def test_can_change_published(self):
        assessment = models.Assessment.objects.get(id=1)
        root = models.Label.get_assessment_root(assessment.id)
        a = root.add_child(name="a", published=False, assessment=assessment)
        a1 = a.add_child(name="a1", published=False, assessment=assessment)

        # can change parent but not child
        status, _ = a.can_change_published()
        assert status is True
        status, _ = a1.can_change_published()
        assert status is False
        a.published = True
        a.save()

        # can change child now
        status, _ = a.can_change_published()
        assert status is True
        status, _ = a1.can_change_published()
        assert status is True
        a1.published = True
        a1.save()

        # can change child but not parent
        status, _ = a.can_change_published()
        assert status is False
        status, _ = a1.can_change_published()
        assert status is True
