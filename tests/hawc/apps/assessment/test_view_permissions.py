import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.assessment.models import Assessment, Log
from hawc.apps.assessment.permissions import AssessmentPermissions

_successful_post = {
    "name": "testing",
    "year": "2013",
    "version": "1",
    "assessment_objective": "<p>Test.</p>",
    "authors": "<p>Test.</p>",
    "noel_name": 0,
    "rob_name": 0,
    "editable": "on",
    "project_manager": ("2",),
    "team_members": ("1", "2"),
    "reviewers": ("1",),
    "epi_version": ("1",),
    "animal_version": ("1",),
    "dtxsids": ("DTXSID7020970",),
}


@pytest.mark.django_db
class TestCreatePermissions:
    def test_success(self):
        # with authentication
        url = reverse("assessment:new")
        c = Client()
        assert c.login(username="pm@hawcproject.org", password="pw") is True
        response = c.get(url)
        assert response.status_code == 200

        n_assessments = Assessment.objects.count()
        with assertTemplateUsed("assessment/assessment_detail.html"):
            response = c.post(url, data=_successful_post, follow=True)
        assert response.status_code == 200
        assert Assessment.objects.count() == n_assessments + 1

    def test_failure(self):
        # without authentication
        url = reverse("assessment:new")
        c = Client()
        resp = c.get(url, follow=True)
        assertTemplateUsed(resp, "registration/login.html")

        resp = c.post(url, _successful_post, follow=True)
        assertTemplateUsed(resp, "registration/login.html")


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
                    url = reverse(view, args=(pk,))
                    response = c.get(url)
                    assert response.status_code == 200

        # anon user should not view
        c = Client()
        for view in views:
            url = reverse(view, args=(db_keys.assessment_working,))
            response = c.get(url)
            assert response.status_code == 403

        # this is public
        for view in views:
            url = reverse(view, args=(db_keys.assessment_final,))
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
            url = reverse("assessment:update", args=(db_keys.assessment_working,))
            with assertTemplateUsed("assessment/assessment_detail.html"):
                response = c.post(url, data=_successful_post, follow=True)
                assert response.status_code == 200

            # check post updates `assessment_final`
            url = reverse("assessment:update", args=(db_keys.assessment_final,))
            with assertTemplateUsed("assessment/assessment_detail.html"):
                response = c.post(url, data=_successful_post, follow=True)
                assert response.status_code == 200

        # rollback in test doesn't clear permissions cache; clear manually
        AssessmentPermissions.clear_cache(db_keys.assessment_working)
        AssessmentPermissions.clear_cache(db_keys.assessment_final)

    def test_failure(self, db_keys):
        clients = (None, "team@hawcproject.org", "reviewer@hawcproject.org")
        for client in clients:
            c = Client()
            if client:
                assert c.login(email=client, password="pw") is True

            for pk in db_keys.assessment_keys:
                url = reverse("assessment:update", args=(pk,))
                with assertTemplateUsed("403.html"):
                    response = c.get(url, follow=True)
                    assert response.status_code == 403
                with assertTemplateUsed("403.html"):
                    response = c.post(url, {"name": "foo manchu"})
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
                url = reverse("assessment:delete", args=(pk,))
                with assertTemplateUsed("403.html"):
                    response = c.get(url, follow=True)
                assert response.status_code == 403

                # check POST
                url = reverse("assessment:update", args=(pk,))
                with assertTemplateUsed("403.html"):
                    response = c.post(url, {"name": "foo manchu"})
                assert response.status_code == 403

    def _test_delete_client_success(self, c, db_keys):
        url = reverse("assessment:delete", args=(db_keys.assessment_working,))
        with assertTemplateUsed("assessment/assessment_home.html"):
            response = c.post(url, follow=True)
        assert response.status_code == 200

        url = reverse("assessment:delete", args=(db_keys.assessment_final,))
        with assertTemplateUsed("assessment/assessment_home.html"):
            response = c.post(url, follow=True)
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


@pytest.mark.django_db
class TestLogViewPermissions:
    def test_assessment_log_list(self):
        url = reverse("assessment:assessment_logs", args=(1,))

        c = Client()
        response = c.get(url)
        assert response.status_code == 403

        assert c.login(email="team@hawcproject.org", password="pw") is True

        response = c.get(url)
        assertTemplateUsed(response, "assessment/assessment_log_list.html")
        assert response.status_code == 200

    def test_log_object_list(self):
        log = Log.objects.get(id=3)
        url = log.get_object_url()

        c = Client()
        response = c.get(url)
        assert response.status_code == 403

        assert c.login(email="team@hawcproject.org", password="pw") is True
        with assertTemplateUsed("assessment/log_object_list.html"):
            response = c.get(url)
            assert response.status_code == 200

    def test_log_detail_page(self):
        log = Log.objects.get(id=2)
        url = log.get_absolute_url()

        c = Client()
        assert c.login(email="pm@hawcproject.org", password="pw") is True
        response = c.get(url)
        assert response.status_code == 403

        assert c.login(email="admin@hawcproject.org", password="pw") is True
        with assertTemplateUsed("assessment/log_detail.html"):
            response = c.get(url)
            assert response.status_code == 200
