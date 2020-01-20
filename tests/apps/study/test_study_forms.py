import re

import pytest
from django.core.urlresolvers import reverse
from django.test.client import Client
from pytest_django.asserts import assertFormError, assertRedirects, assertTemplateUsed


@pytest.mark.django_db
def test_study_forms(study_data):
    c = Client()
    assert c.login(username="team@team.com", password="pw") is True

    new_study_url = reverse(
        "study:new_ref", kwargs={"pk": study_data["assessment"]["assessment_working"].id}
    )
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
    assertRedirects(response, reverse("study:detail", kwargs={"pk": pk}))

    # can't create a new study citation field that already exists
    response = c.post(new_study_url, study_dict)
    assertFormError(
        response, "form", None, "Error- short-citation name must be unique for assessment.",
    )

    # can change an existing study citation field to a different type
    response = c.post(reverse("study:update", kwargs={"pk": pk}), study_dict)
    assert response.status_code in [200, 302]
    assertTemplateUsed("study/study_detail.html")

    # can create a new study in different assessment
    c.logout()
    assert c.login(username="sudo@sudo.com", password="pw") is True

    response = c.post(
        reverse("study:new_ref", kwargs={"pk": study_data["assessment"]["assessment_final"].id}),
        study_dict,
    )
    pk = re.findall(r"/study/(\d+)/$", response["location"])
    pk = int(pk[0])
    assertRedirects(response, reverse("study:detail", kwargs={"pk": pk}))
