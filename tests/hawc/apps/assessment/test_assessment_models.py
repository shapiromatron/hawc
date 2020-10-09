import pytest

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
