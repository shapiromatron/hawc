import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.animalv2.models import Experiment

_successful_post = {
    "name": "exp name",
    "design": "AA",
    "has_multiple_generations": False,
    "guideline_compliance": "test compliance",
    "comments": "<p>test comments</p>",
}


@pytest.mark.django_db
class TestCreatePermissions:
    def test_success(self, db_keys):
        # with authentication
        url = reverse("animalv2:experiment_create", kwargs={"pk": db_keys.study_working})
        c = Client()
        assert c.login(username="admin@hawcproject.org", password="pw") is True
        response = c.get(url)
        assert response.status_code == 200

        n_experiments = Experiment.objects.count()

        with assertTemplateUsed("animalv2/experiment_detail.html"):
            response = c.post(
                url,
                data=_successful_post,
                follow=True,
            )
            assert Experiment.objects.count() == n_experiments + 1
            n_experiments += 1
            assert response.status_code == 200

    def test_failure(self, db_keys):
        # without authentication
        url = reverse("animalv2:experiment_create", kwargs={"pk": db_keys.study_working})
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
            response = c.get(
                reverse(
                    "animalv2:experiment_detail",
                    kwargs={"pk": db_keys.animalv2_experiment},
                )
            )
            assert response.status_code == 200

        # anon user should not view
        c = Client()
        url = reverse("animalv2:experiment_detail", kwargs={"pk": db_keys.animalv2_experiment})
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
            view = "animalv2:experiment_update"
            pk = db_keys.animalv2_experiment
            response = c.get(reverse(view, args=(pk,)))
            assert response.status_code == 200

            # check post updates `animalv2_experiment`
            with assertTemplateUsed("animalv2/experiment_detail.html"):
                response = c.post(
                    reverse(
                        "animalv2:experiment_update",
                        kwargs={"pk": db_keys.animalv2_experiment},
                    ),
                    data=_successful_post,
                    follow=True,
                )
                assert response.status_code == 200

    def test_failure(self, db_keys):
        c = Client()

        view = "animalv2:experiment_update"
        with assertTemplateUsed("403.html"):
            response = c.get(
                reverse(
                    view,
                    kwargs={"pk": db_keys.animalv2_experiment},
                ),
                follow=True,
            )
            assert response.status_code == 403

        # check POST
        with assertTemplateUsed("403.html"):
            response = c.post(
                reverse(
                    "animalv2:experiment_update",
                    kwargs={"pk": db_keys.animalv2_experiment},
                ),
                {"name": "bad data"},
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
            view = "animalv2:experiment_delete"
            response = c.get(reverse(view, kwargs={"pk": db_keys.animalv2_experiment}))
            assert response.status_code == 200

    def test_failure(self, db_keys):
        c = Client()

        view = "animalv2:experiment_delete"
        with assertTemplateUsed("403.html"):
            response = c.get(reverse(view, kwargs={"pk": db_keys.animalv2_experiment}), follow=True)
            assert response.status_code == 403

        # check POST
        with assertTemplateUsed("403.html"):
            response = c.post(
                reverse("animalv2:experiment_update", kwargs={"pk": db_keys.animalv2_experiment}),
                {"name": "bad data"},
            )
            assert response.status_code == 403
