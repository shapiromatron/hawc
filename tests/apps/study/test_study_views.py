import re

import pytest
from django.core.urlresolvers import reverse
from django.test.client import Client
from pytest_django.asserts import assertTemplateUsed


@pytest.mark.django_db
def test_study_read_success(study_data):
    clients = ["sudo@sudo.com", "pm@pm.com", "team@team.com", "rev@rev.com"]
    views = [
        reverse("study:list", kwargs={"pk": study_data["assessment"]["assessment_working"].id}),
        reverse("study:detail", kwargs={"pk": study_data["study"]["study_working"].id}),
        reverse("study:list", kwargs={"pk": study_data["assessment"]["assessment_final"].id}),
        reverse("study:detail", kwargs={"pk": study_data["study"]["study_final"].id}),
    ]

    for client in clients:
        c = Client()
        assert c.login(username=client, password="pw") is True
        for view in views:
            response = c.get(view)
            assert response.status_code == 200


@pytest.mark.django_db
def test_study_read_failure(study_data):
    # anonymous user
    c = Client()
    views = [
        {
            "view": reverse(
                "study:list", kwargs={"pk": study_data["assessment"]["assessment_working"].id}
            ),
            "status": 403,
        },
        {
            "view": reverse("study:detail", kwargs={"pk": study_data["study"]["study_working"].id}),
            "status": 403,
        },
        {
            "view": reverse(
                "study:list", kwargs={"pk": study_data["assessment"]["assessment_final"].id}
            ),
            "status": 200,
        },
        {
            "view": reverse("study:detail", kwargs={"pk": study_data["study"]["study_final"].id}),
            "status": 200,
        },
    ]
    for view in views:
        response = c.get(view["view"])
        assert response.status_code == view["status"]


@pytest.mark.django_db
def test_study_crud_success(study_data):
    # Check to ensure that sudo, pm and team have CRUD permissions.
    # Create a new study, edit, view prior versions, and delete. Test both
    # GET and POST when appropriate.
    clients = ["sudo@sudo.com", "pm@pm.com", "team@team.com"]
    for client in clients:
        c = Client()
        assert c.login(username=client, password="pw") is True

        # create new
        response = c.get(
            reverse(
                "study:new_ref", kwargs={"pk": study_data["assessment"]["assessment_working"].id}
            )
        )
        assert response.status_code == 200
        response = c.post(
            reverse(
                "study:new_ref", kwargs={"pk": study_data["assessment"]["assessment_working"].id}
            ),
            {
                "assessment": study_data["assessment"]["assessment_working"].id,
                "short_citation": "foo et al.",
                "full_citation": "cite",
                "bioassay": True,
                "coi_reported": 0,
            },
        )
        assert response.status_code == 302
        assertTemplateUsed("study/study_detail.html")
        pk = int(re.findall(r"/study/(\d+)/$", response["location"])[0])

        # edit
        response = c.get(reverse("study:update", kwargs={"pk": pk}))
        assert response.status_code == 200
        response = c.post(
            reverse("study:update", kwargs={"pk": pk}),
            {
                "assessment": study_data["assessment"]["assessment_working"].id,
                "citation": "foo et al.",
                "full_citation": "cite",
            },
        )
        assert response.status_code in [200, 302]
        assertTemplateUsed("study/study_detail.html")

        # view versions
        response = c.get(reverse("study:update", kwargs={"pk": pk}))
        assert response.status_code == 200

        # delete
        response = c.get(reverse("study:delete", kwargs={"pk": pk}))
        assert response.status_code == 200
        response = c.post(reverse("study:delete", kwargs={"pk": pk}))
        assert response.status_code == 302


@pytest.mark.django_db
def test_uf_crud_failure(study_data):
    # Check to ensure that rev and None don't have CRUD permissions.
    # Attempt to create a new study, edit, view prior versions, and delete.
    # Test both GET and POST when appropriate.

    # first test working scenario
    users = ["rev@rev.com", None]
    views = [
        reverse("study:new_ref", kwargs={"pk": study_data["assessment"]["assessment_working"].id}),
        reverse("study:update", kwargs={"pk": study_data["study"]["study_working"].id}),
        reverse("study:delete", kwargs={"pk": study_data["study"]["study_working"].id}),
    ]

    for user in users:
        c = Client()
        if user:
            assert c.login(username=user, password="pw") is True

        for view in views:
            response = c.get(view)
            response.status_code == 403
            response = c.post(view)
            response.status_code in [403, 405]

    # next check that all people (except sudo) cannot edit a final study
    users = ["pm@pm.com", "team@team.com", "rev@rev.com", None]
    views = [
        reverse("study:new_ref", kwargs={"pk": study_data["assessment"]["assessment_final"].id}),
        reverse("study:update", kwargs={"pk": study_data["study"]["study_final"].id}),
        reverse("study:delete", kwargs={"pk": study_data["study"]["study_final"].id}),
    ]

    for user in users:
        c = Client()
        if user:
            assert c.login(username=user, password="pw") is True

        for view in views:
            response = c.get(view)
            assert response.status_code == 403
            response = c.post(view)
            assert response.status_code in [403, 405]
