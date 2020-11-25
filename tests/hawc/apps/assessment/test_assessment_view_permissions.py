import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.assessment.models import Assessment

_successful_post = {
    "name": "testing",
    "year": "2013",
    "version": "1",
    "public": "off",
    "noel_name": 0,
    "rob_name": 0,
    "editable": "on",
    "project_manager_0": ("2",),
    "project_manager_1": ("2",),
    "team_members_0": ("1", "2"),
    "team_members_1": ("1", "2"),
    "reviewers_0": ("1",),
    "reviewers_1": ("1",),
    "dtxsids_0": ("DTXSID7020970",),
    "dtxsids_1": ("DTXSID7020970",),
}


@pytest.mark.django_db
class TestCreatePermissions:
    def test_success(self):
        # with authentication
        url = reverse("assessment:new")
        c = Client()
        assert c.login(username="reviewer@hawcproject.org", password="pw") is True
        response = c.get(url)
        assert response.status_code == 200

        n_assessments = Assessment.objects.count()
        with assertTemplateUsed("assessment/assessment_detail.html"):
            response = c.post(url, data=_successful_post, follow=True,)
            assert Assessment.objects.count() == n_assessments + 1
            n_assessments += 1
            assert response.status_code == 200

    def test_failure(self):
        # without authentication
        url = reverse("assessment:new")
        c = Client()
        with assertTemplateUsed("registration/login.html"):
            c.get(url, follow=True)

        with assertTemplateUsed("registration/login.html"):
            c.post(url, _successful_post, follow=True)


@pytest.mark.django_db
class TestDetailPermissions:
    def test_detail(self, db_keys):
        # these users should have permission
        users = (
            "admin@hawcproject.org",
            "pm@hawcproject.org",
            "team@hawcproject.org",
            "reviewer@hawcproject.org",
        )
        views = ("assessment:detail", "assessment:api:assessment-detail")
        for user in users:
            c = Client()
            assert c.login(email=user, password="pw") is True
            for view in views:
                for pk in db_keys.assessment_keys:
                    response = c.get(reverse(view, args=(pk,)))
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
class TestEditPermissions:
    def test_success(self, db_keys):
        clients = ("admin@hawcproject.org", "pm@hawcproject.org")
        for client in clients:
            c = Client()
            assert c.login(email=client, password="pw") is True

            # django template views
            view = "assessment:update"
            pk = db_keys.assessment_working
            response = c.get(reverse(view, args=(pk,)))
            assert response.status_code == 200

            # check post updates `assessment_working`
            with assertTemplateUsed("assessment/assessment_detail.html"):
                response = c.post(
                    reverse("assessment:update", kwargs={"pk": db_keys.assessment_working},),
                    data=_successful_post,
                    follow=True,
                )
                assert response.status_code == 200

            # check post updates `assessment_final`
            with assertTemplateUsed("assessment/assessment_detail.html"):
                response = c.post(
                    reverse("assessment:update", kwargs={"pk": db_keys.assessment_final},),
                    data=_successful_post,
                    follow=True,
                )
                assert response.status_code == 200

    def test_failure(self, db_keys):
        clients = (None, "team@hawcproject.org", "reviewer@hawcproject.org")
        for client in clients:
            c = Client()
            if client:
                assert c.login(email=client, password="pw") is True

            for pk in db_keys.assessment_keys:
                view = "assessment:update"
                with assertTemplateUsed("403.html"):
                    response = c.get(reverse(view, args=(pk,)), follow=True)
                    assert response.status_code == 403

                # check POST
                with assertTemplateUsed("403.html"):
                    response = c.post(
                        reverse("assessment:update", args=(pk,)), {"name": "foo manchu"},
                    )
                    assert response.status_code == 403


@pytest.mark.django_db
class TestDeletePermissions:
    def test_success(self, db_keys):
        clients = ("admin@hawcproject.org", "pm@hawcproject.org")
        for client in clients:
            c = Client()
            assert c.login(email=client, password="pw") is True

            # django template views
            view = "assessment:delete"
            for pk in db_keys.assessment_keys:
                response = c.get(reverse(view, args=(pk,)))
                assert response.status_code == 200

    def test_failure(self, db_keys):
        clients = (None, "team@hawcproject.org", "reviewer@hawcproject.org")
        for client in clients:
            c = Client()
            if client:
                assert c.login(email=client, password="pw") is True
            for pk in db_keys.assessment_keys:
                view = "assessment:delete"
                with assertTemplateUsed("403.html"):
                    response = c.get(reverse(view, args=(pk,)), follow=True)
                    assert response.status_code == 403

                # check POST
                with assertTemplateUsed("403.html"):
                    response = c.post(
                        reverse("assessment:update", args=(pk,)), {"name": "foo manchu"},
                    )
                    assert response.status_code == 403

    def _test_delete_client_success(self, c, db_keys):
        with assertTemplateUsed("assessment/assessment_home.html"):
            response = c.post(
                reverse("assessment:delete", args=(db_keys.assessment_working,)), follow=True,
            )
            assert response.status_code == 200

        with assertTemplateUsed("assessment/assessment_home.html"):
            response = c.post(
                reverse("assessment:delete", args=(db_keys.assessment_final,)), follow=True
            )
            assert response.status_code == 200

    def test_delete_superuser(self, db_keys):
        c = Client()
        assert c.login(email="admin@hawcproject.org", password="pw") is True
        self._test_delete_client_success(c, db_keys)

    def test_delete_project_manager(self, db_keys):
        c = Client()
        assert c.login(email="pm@hawcproject.org", password="pw") is True
        self._test_delete_client_success(c, db_keys)

    def test_delete_forbidden(self, db_keys):
        clients = (None, "team@hawcproject.org", "reviewer@hawcproject.org")
        for client in clients:
            c = Client()
            if client:
                assert c.login(email=client, password="pw") is True
            for pk in db_keys.assessment_keys:
                response = c.post(reverse("assessment:delete", args=(pk,)))
                assert response.status_code == 403
