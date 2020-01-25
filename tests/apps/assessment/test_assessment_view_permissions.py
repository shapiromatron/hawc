import pytest
from django.core.urlresolvers import reverse
from django.test.client import Client
from pytest_django.asserts import assertTemplateUsed


@pytest.mark.django_db
def test_new_success():
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
                },
            )
            assert response.status_code in [200, 302]
            assertTemplateUsed("assessment/assessment_detail.html")


@pytest.mark.django_db
def test_new_forbidden():
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
def test_detail_success():
    users = ("sudo@sudo.com", "pm@pm.com", "team@team.com", "rev@rev.com")
    views = ("assessment:detail",)
    pks = (1, 2)
    for user in users:
        c = Client()
        assert c.login(email=user, password="pw") is True
        for view in views:
            for pk in pks:
                response = c.get(reverse(view, kwargs={"pk": pk}))
                assert response.status_code == 200


@pytest.mark.django_db
def test_detail_view_public():
    c = Client()
    response = c.get(reverse("assessment:detail", kwargs={"pk": 1},))
    assert response.status_code == 403

    response = c.get(reverse("assessment:detail", kwargs={"pk": 2}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_edit_view_success():
    clients = ("sudo@sudo.com", "pm@pm.com")
    views = ("assessment:update", "assessment:delete")
    pks = (1, 2)
    for client in clients:
        c = Client()
        assert c.login(email=client, password="pw") is True

        for view in views:
            for pk in pks:
                response = c.get(reverse(view, kwargs={"pk": pk}))
                assert response.status_code == 200

        # check post updates
        response = c.post(reverse("assessment:update", kwargs={"pk": 1},), {"name": "foo manchu"},)
        assertTemplateUsed("assessment/assessment_detail.html")
        assert response.status_code == 200

        response = c.post(reverse("assessment:update", kwargs={"pk": 2},), {"name": "foo manchu"},)
        assertTemplateUsed("assessment/assessment_detail.html")
        assert response.status_code == 200


@pytest.mark.django_db
def test_edit_view_forbidden():
    clients = (None, "team@team.com", "rev@rev.com")
    views = ("assessment:update", "assessment:delete")
    pks = (1, 2)
    for client in clients:
        c = Client()
        if client:
            assert c.login(email=client, password="pw") is True
        for pk in pks:
            for view in views:
                response = c.get(reverse(view, kwargs={"pk": pk}))
                assert response.status_code == 403

            # check POST
            response = c.post(
                reverse("assessment:update", kwargs={"pk": pk}), {"name": "foo manchu"},
            )
            assert response.status_code == 403


@pytest.mark.django_db
def test_delete_superuser():
    c = Client()
    assert c.login(email="sudo@sudo.com", password="pw") is True

    response = c.post(reverse("assessment:delete", kwargs={"pk": 1},))
    assert response.status_code == 302
    assertTemplateUsed("assessment/assessment_list.html")

    response = c.post(reverse("assessment:delete", kwargs={"pk": 2}))
    assert response.status_code == 302
    assertTemplateUsed("assessment/assessment_list.html")


@pytest.mark.django_db
def test_delete_project_manager(test_db):
    c = Client()
    assert c.login(email="pm@pm.com", password="pw") is True

    response = c.post(reverse("assessment:delete", kwargs={"pk": 1},))
    assert response.status_code == 302
    assertTemplateUsed("assessment/assessment_list.html")

    response = c.post(reverse("assessment:delete", kwargs={"pk": 2}))
    assert response.status_code == 302
    assertTemplateUsed("assessment/assessment_list.html")


@pytest.mark.django_db
def test_delete_forbidden():
    clients = (None, "team@team.com", "rev@rev.com")
    pks = (1, 2)
    for client in clients:
        c = Client()
        if client:
            assert c.login(email=client, password="pw") is True
        for pk in pks:
            response = c.post(reverse("assessment:delete", kwargs={"pk": pk}))
            assert response.status_code == 403
