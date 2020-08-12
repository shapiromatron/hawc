import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed


@pytest.mark.django_db
def test_create_assessment():
    # expected success
    users = ("sudo@sudo.com", "pm@pm.com", "team@team.com", "rev@rev.com")
    views = ("assessment:new",)
    for user in users:
        c = Client()
        assert c.login(username=user, password="pw") is True
        for view in views:
            response = c.get(reverse(view))
            assert response.status_code == 200
            response = c.post(
                reverse(view),
                {
                    "name": "testing",
                    "year": "2013",
                    "version": "1",
                    "public": "off",
                    "editable": "on",
                    "project_manager": ("1"),
                    "team_members": ("1", "2"),
                    "reviewers": ("1"),
                    "dtxsids": ("DTXSID7020970",),
                },
            )
            assert response.status_code in [200, 302]
            assertTemplateUsed("assessment/assessment_detail.html")

    # expected failure
    clients = (None,)
    views = ("assessment:new",)
    for client in clients:
        c = Client()
        assert c.login(email=client, password="pw") is False
        for view in views:
            c.get(reverse(view))
            assertTemplateUsed("registration/login.html")
            c.post(
                reverse(view),
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
            assertTemplateUsed("registration/login.html")


@pytest.mark.django_db
def test_detail(db_keys):
    # these users should have permission
    users = ("sudo@sudo.com", "pm@pm.com", "team@team.com", "rev@rev.com")
    views = ("assessment:detail", "assessment:api:assessment-detail")
    for user in users:
        c = Client()
        assert c.login(email=user, password="pw") is True
        for view in views:
            for pk in db_keys.assessment_keys:
                response = c.get(reverse(view, kwargs={"pk": pk}))
                assert response.status_code == 200

    # anon user should not view
    c = Client()
    for view in views:
        url = reverse(view, kwargs={"pk": db_keys.assessment_working})
        response = c.get(url)
        assert response.status_code == 403

    # this is public
    for view in views:
        url = reverse(view, kwargs={"pk": db_keys.assessment_final})
        response = c.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
def test_edit_view_success_template(db_keys):
    clients = ("sudo@sudo.com", "pm@pm.com")
    for client in clients:
        c = Client()
        assert c.login(email=client, password="pw") is True

        # django template views
        for view in ("assessment:update", "assessment:delete"):
            for pk in db_keys.assessment_keys:
                response = c.get(reverse(view, kwargs={"pk": pk}))
                assert response.status_code == 200

        # check post updates
        response = c.post(
            reverse("assessment:update", kwargs={"pk": db_keys.assessment_working},),
            {"name": "foo manchu"},
        )
        assertTemplateUsed("assessment/assessment_detail.html")
        assert response.status_code == 200

        response = c.post(
            reverse("assessment:update", kwargs={"pk": db_keys.assessment_final},),
            {"name": "foo manchu"},
        )
        assertTemplateUsed("assessment/assessment_detail.html")
        assert response.status_code == 200


@pytest.mark.django_db
def test_edit_view_forbidden(db_keys):
    clients = (None, "team@team.com", "rev@rev.com")
    for client in clients:
        c = Client()
        if client:
            assert c.login(email=client, password="pw") is True
        for pk in db_keys.assessment_keys:
            for view in ("assessment:update", "assessment:delete"):
                response = c.get(reverse(view, kwargs={"pk": pk}))
                assert response.status_code == 403

            # check POST
            response = c.post(
                reverse("assessment:update", kwargs={"pk": pk}), {"name": "foo manchu"},
            )
            assert response.status_code == 403


@pytest.mark.django_db
def test_delete_superuser(db_keys):
    c = Client()
    assert c.login(email="sudo@sudo.com", password="pw") is True

    response = c.post(reverse("assessment:delete", kwargs={"pk": db_keys.assessment_working},))
    assert response.status_code == 302
    assertTemplateUsed("assessment/assessment_list.html")

    response = c.post(reverse("assessment:delete", kwargs={"pk": db_keys.assessment_final}))
    assert response.status_code == 302
    assertTemplateUsed("assessment/assessment_list.html")


@pytest.mark.django_db
def test_delete_project_manager(db_keys):
    c = Client()
    assert c.login(email="pm@pm.com", password="pw") is True

    response = c.post(reverse("assessment:delete", kwargs={"pk": db_keys.assessment_working},))
    assert response.status_code == 302
    assertTemplateUsed("assessment/assessment_list.html")

    response = c.post(reverse("assessment:delete", kwargs={"pk": db_keys.assessment_final}))
    assert response.status_code == 302
    assertTemplateUsed("assessment/assessment_list.html")


@pytest.mark.django_db
def test_delete_forbidden(db_keys):
    clients = (None, "team@team.com", "rev@rev.com")
    for client in clients:
        c = Client()
        if client:
            assert c.login(email=client, password="pw") is True
        for pk in db_keys.assessment_keys:
            response = c.post(reverse("assessment:delete", kwargs={"pk": pk}))
            assert response.status_code == 403
