import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from ..test_utils import check_200, get_client


@pytest.mark.django_db
def test_study_read_success(db_keys):
    clients = [
        ("admin@hawcproject.org", (200, 200, 200, 200)),
        ("pm@hawcproject.org", (200, 200, 200, 200)),
        ("team@hawcproject.org", (200, 200, 200, 200)),
        ("reviewer@hawcproject.org", (200, 403, 200, 200)),
    ]
    views = [
        reverse("study:list", kwargs={"pk": db_keys.assessment_working}),
        reverse("study:detail", kwargs={"pk": db_keys.study_working}),
        reverse("study:list", kwargs={"pk": db_keys.assessment_final}),
        reverse("study:detail", kwargs={"pk": db_keys.study_final_bioassay}),
    ]

    for client, codes in clients:
        c = Client()
        assert c.login(username=client, password="pw") is True
        for view, code in zip(views, codes, strict=True):
            response = c.get(view)
            assert response.status_code == code


@pytest.mark.django_db
def test_study_read_failure(db_keys):
    # anonymous user
    c = Client()
    views = [
        {"view": reverse("study:list", kwargs={"pk": db_keys.assessment_working}), "status": 403},
        {"view": reverse("study:detail", kwargs={"pk": db_keys.study_working}), "status": 403},
        {"view": reverse("study:list", kwargs={"pk": db_keys.assessment_final}), "status": 200},
        {
            "view": reverse("study:detail", kwargs={"pk": db_keys.study_final_bioassay}),
            "status": 200,
        },
    ]
    for view in views:
        response = c.get(view["view"])
        assert response.status_code == view["status"]


@pytest.mark.django_db
def test_study_crud_success(db_keys):
    # Check to ensure that sudo, pm and team have CRUD permissions.
    # Create a new study, edit, view prior versions, and delete. Test both
    # GET and POST when appropriate.
    clients = ["admin@hawcproject.org", "pm@hawcproject.org", "team@hawcproject.org"]
    for client in clients:
        c = Client()
        assert c.login(username=client, password="pw") is True

        # create new
        response = c.get(reverse("study:new_ref", kwargs={"pk": db_keys.assessment_working}))
        assert response.status_code == 200

        with assertTemplateUsed("study/study_detail.html"):
            response = c.post(
                reverse("study:new_ref", kwargs={"pk": db_keys.assessment_working}),
                {
                    "assessment": db_keys.assessment_working,
                    "short_citation": "foo et al.",
                    "full_citation": "cite",
                    "bioassay": True,
                    "coi_reported": 0,
                },
                follow=True,
            )

        assert response.status_code == 200
        pk = response.context["object"].id

        # edit
        response = c.get(reverse("study:update", args=(pk,)))
        assert response.status_code == 200

        with assertTemplateUsed("study/study_detail.html"):
            response = c.post(
                reverse("study:update", args=(pk,)),
                {
                    "assessment": db_keys.assessment_working,
                    "short_citation": "foo et al.",
                    "full_citation": "cite",
                    "coi_reported": 0,
                },
                follow=True,
            )
            assert response.status_code == 200

        # delete
        response = c.get(reverse("study:delete", args=(pk,)))
        assertTemplateUsed(response, "study/study_confirm_delete.html")
        assert response.status_code == 200

        response = c.post(reverse("study:delete", args=(pk,)), follow=True)
        assertTemplateUsed(response, "study/study_list.html")
        assert response.status_code == 200


@pytest.mark.django_db
def test_uf_crud_failure(db_keys):
    # Check to ensure that rev and None don't have CRUD permissions.
    # Attempt to create a new study, edit, view prior versions, and delete.
    # Test both GET and POST when appropriate.

    # first test working scenario
    users = ["reviewer@hawcproject.org", None]
    views = [
        reverse("study:new_ref", kwargs={"pk": db_keys.assessment_working}),
        reverse("study:update", kwargs={"pk": db_keys.study_working}),
        reverse("study:delete", kwargs={"pk": db_keys.study_working}),
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

    # next check that all people (except sudo) cannot edit a final study
    users = ["pm@hawcproject.org", "team@hawcproject.org", "reviewer@hawcproject.org", None]
    views = [
        reverse("study:new_ref", kwargs={"pk": db_keys.assessment_final}),
        reverse("study:update", kwargs={"pk": db_keys.study_final_bioassay}),
        reverse("study:delete", kwargs={"pk": db_keys.study_final_bioassay}),
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


@pytest.mark.django_db
def test_get_200():
    client = get_client("pm")
    main = 1

    url_redirect = reverse("study:rob_redirect", args=(main,))
    assert client.get(url_redirect).status_code == 301
    url_toggle_lock = reverse("study:toggle-lock", args=(main,))
    assert client.get(url_toggle_lock).status_code == 302

    urls = [
        reverse("study:new_ref", args=(main,)),
        reverse("study:create_from_identifier", args=(main,)),
        reverse("study:attachment_create", args=(main,)),
        reverse("study:list", args=(main,)),
        reverse("study:detail", args=(main,)),
        reverse("study:delete", args=(main,)),
        reverse("study:new_study", args=(3,)),
    ]
    for url in urls:
        check_200(client, url)
