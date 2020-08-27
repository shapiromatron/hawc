import pytest

from hawc.apps.assessment.models import Blog


@pytest.mark.django_db
def test_blog_save():
    # on save content is rendered to html and saved as rendered_content
    blog = Blog.objects.create(content="Test content")
    assert blog.rendered_content.strip() == "<p>Test content</p>"

    # markdown should be correctly rendered to html
    blog = Blog.objects.create(content="# Test header")
    assert blog.rendered_content.strip() == "<h1>Test header</h1>"
