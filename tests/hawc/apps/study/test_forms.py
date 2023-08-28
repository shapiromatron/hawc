import re

import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects, assertTemplateUsed

from hawc.apps.common.forms import ASSESSMENT_UNIQUE_MESSAGE


@pytest.mark.django_db
def test_study_forms(db_keys):
    c = Client()
    assert c.login(username="team@hawcproject.org", password="pw") is True

    new_study_url = reverse("study:new_ref", kwargs={"pk": db_keys.assessment_working})
    study_dict = {
        "short_citation": "foo et al.",
        "full_citation": "cite",
        "bioassay": True,
        "coi_reported": 0,
    }

    # can create a new study field
    response = c.post(new_study_url, study_dict)
    pk = re.findall(r"/study/(\d+)/$", response["location"])
    pk = int(pk[0])
    assertRedirects(response, reverse("study:detail", args=(pk,)))

    # can't create a new study citation field that already exists
    response = c.post(new_study_url, study_dict)
    assertFormError(response.context["form"], "short_citation", ASSESSMENT_UNIQUE_MESSAGE)

    # can change an existing study citation field to a different type
    with assertTemplateUsed("study/study_detail.html"):
        response = c.post(reverse("study:update", args=(pk,)), study_dict, follow=True)
        assert response.status_code == 200

    # can create a new study in different assessment
    c.logout()
    assert c.login(username="admin@hawcproject.org", password="pw") is True

    response = c.post(
        reverse("study:new_ref", kwargs={"pk": db_keys.assessment_final}),
        study_dict,
    )
    pk = re.findall(r"/study/(\d+)/$", response["location"])
    pk = int(pk[0])
    assertRedirects(response, reverse("study:detail", args=(pk,)))
