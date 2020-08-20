import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.assessment.models import Blog


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
def test_blog_save():
    # on save content is rendered to html and saved as rendered_content
    blog = Blog.objects.create(content="Test content")
    assert blog.rendered_content.strip() == "<p>Test content</p>"

    # markdown should be correctly rendered to html
    blog = Blog.objects.create(content="# Test header")
    assert blog.rendered_content.strip() == "<h1>Test header</h1>"
