import pytest
from django.core.urlresolvers import reverse
from django.test.client import Client
from pytest_django.asserts import assertTemplateUsed


@pytest.mark.django_db
def test_assessment_creation(assessment_data):
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
