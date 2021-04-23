import pytest
from django.core.cache import cache
from django.test.client import RequestFactory

from hawc.apps.assessment import models
from hawc.apps.assessment.models import Blog


@pytest.mark.django_db
class TestJob:
    def test_job_success(self, db_keys):
        job = models.Job.objects.create(job=models.JobType.TEST)
        ran_job = models.Job.objects.get(pk=job.task_id)

        assert ran_job.status == models.JobStatus.SUCCESS
        assert ran_job.result.get("data") == "SUCCESS"

    def test_job_failure(self, db_keys):
        job = models.Job.objects.create(job=models.JobType.TEST, kwargs={"fail": True})
        ran_job = models.Job.objects.get(pk=job.task_id)

        assert ran_job.status == models.JobStatus.FAILURE
        assert ran_job.result.get("error") == "FAILURE"


@pytest.mark.django_db
def test_blog_save():
    # on save content is rendered to html and saved as rendered_content
    blog = Blog.objects.create(content="Test content")
    assert blog.rendered_content.strip() == "<p>Test content</p>"

    # markdown should be correctly rendered to html
    blog = Blog.objects.create(content="# Test header")
    assert blog.rendered_content.strip() == "<h1>Test header</h1>"


class TestContent:
    @pytest.mark.django_db
    def test_rendered_page(self):
        rf = RequestFactory()
        request = rf.get("/")
        page = models.Content.rendered_page(models.ContentTypeChoices.HOMEPAGE, request, {})
        assert page == "<h1>Welcome to HAWC</h1>"
        page = models.Content.rendered_page(models.ContentTypeChoices.ABOUT, request, {})
        assert page == "<h1>About HAWC</h1>"

    @pytest.mark.django_db
    def test_cache_lifecycle(self):
        rf = RequestFactory()
        request = rf.get("/")
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
