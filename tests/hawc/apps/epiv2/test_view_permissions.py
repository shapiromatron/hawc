import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.epiv2.models import Design

_successful_post = {
    "study_design": "CC",
    "source": "GP",
    "age_profile": "AD",
    "age_description": "10-15 yrs",
    "sex": "B",
    "race": "Not specified but likely primarily Asian",
    "summary": "Case-control study of asthma in children",
    "study_name": "Genetic and Biomarkers study for Childhood Asthma",
    "countries": "2",
    "region": "northern Taiwan",
    "years": "2009-2010",
    "participant_n": "456",
    "criteria": "<p>Criteria here.</p>",
    "comments": "<p>Comments here.</p>",
}


@pytest.mark.django_db
class TestCreatePermissions:
    def test_success(self, db_keys):
        # with authentication
        url = reverse("epiv2:design_create", kwargs={"pk": db_keys.study_working})
        c = Client()
        assert c.login(username="admin@hawcproject.org", password="pw") is True
        response = c.get(url)
        assert response.status_code == 200

        n_designs = Design.objects.count()
        with assertTemplateUsed("epiv2/design_update.html"):
            response = c.post(url, data=_successful_post, follow=True,)
            assert Design.objects.count() == n_designs + 1
            n_designs += 1
            assert response.status_code == 200

    def test_failure(self, db_keys):
        # without authentication
        url = reverse("epiv2:design_create", kwargs={"pk": db_keys.study_working})
        c = Client()
        with assertTemplateUsed("403.html"):
            c.get(url, follow=True)

        with assertTemplateUsed("403.html"):
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
        for user in users:
            c = Client()
            assert c.login(email=user, password="pw") is True
            response = c.get(reverse("epiv2:design_detail", kwargs={"pk": db_keys.epiv2_design}))
            assert response.status_code == 200

        # anon user should not view
        c = Client()
        url = reverse("epiv2:design_detail", kwargs={"pk": db_keys.epiv2_design})
        response = c.get(url)
        assert response.status_code == 403


@pytest.mark.django_db
class TestUpdatePermissions:
    def test_success(self, db_keys):
        clients = ("admin@hawcproject.org", "pm@hawcproject.org")
        for client in clients:
            c = Client()
            assert c.login(email=client, password="pw") is True

            # django template views
            view = "epiv2:design_update"
            pk = db_keys.epiv2_design
            response = c.get(reverse(view, args=(pk,)))
            assert response.status_code == 200

            # check post updates `epiv2_design`
            with assertTemplateUsed("epiv2/design_detail.html"):
                response = c.post(
                    reverse("epiv2:design_update", kwargs={"pk": db_keys.epiv2_design},),
                    data=_successful_post,
                    follow=True,
                )
                assert response.status_code == 200

    def test_failure(self, db_keys):
        c = Client()

        view = "epiv2:design_update"
        with assertTemplateUsed("403.html"):
            response = c.get(reverse(view, kwargs={"pk": db_keys.epiv2_design},), follow=True)
            assert response.status_code == 403

        # check POST
        with assertTemplateUsed("403.html"):
            response = c.post(
                reverse("epiv2:design_update", kwargs={"pk": db_keys.epiv2_design},),
                {"name": "foo manchu"},
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
            view = "epiv2:design_delete"
            response = c.get(reverse(view, kwargs={"pk": db_keys.epiv2_design}))
            assert response.status_code == 200

    def test_failure(self, db_keys):
        c = Client()

        view = "epiv2:design_delete"
        with assertTemplateUsed("403.html"):
            response = c.get(reverse(view, kwargs={"pk": db_keys.epiv2_design}), follow=True)
            assert response.status_code == 403

        # check POST
        with assertTemplateUsed("403.html"):
            response = c.post(
                reverse("epiv2:design_update", kwargs={"pk": db_keys.epiv2_design}),
                {"name": "foo manchu"},
            )
            assert response.status_code == 403
