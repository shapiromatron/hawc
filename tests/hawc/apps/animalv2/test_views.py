import pytest
from django.test.client import Client
from django.urls import reverse

from hawc.apps.animalv2 import models

from ..test_utils import check_200, check_403, get_client, get_first


@pytest.mark.django_db
class TestViewPermissions:
    def test_success(self, db_keys):
        clients = [
            "admin@hawcproject.org",
            "pm@hawcproject.org",
            "team@hawcproject.org",
            "reviewer@hawcproject.org",
        ]
        views = [
            reverse("animalv2:studylevelvalues", args=(db_keys.study_working,)),
        ]
        for client in clients:
            c = Client()
            assert c.login(username=client, password="pw") is True
            for view in views:
                response = c.get(view)
                assert response.status_code == 200

    def test_failure(self, db_keys):
        # anonymous user
        c = Client()
        views = [
            (reverse("animalv2:studylevelvalues", args=(db_keys.study_working,)), 403),
        ]
        for url, status in views:
            response = c.get(url)
            assert response.status_code == status


@pytest.mark.django_db
class TestExperimentView:
    def test_permission(self, db_keys):
        experiment = get_first(models.Experiment)
        url = reverse("animalv2:experiment_detail", args=(experiment.id,))
        client = get_client()
        check_403(client, url)

        url = reverse("animalv2:experiment_update", args=(experiment.id,))
        check_403(client, url)

    def test_success(self, db_keys):
        random_experiment = get_first(models.Experiment)
        url = reverse("animalv2:experiment_detail", args=(random_experiment.id,))
        client = get_client("pm")
        response = check_200(client, url)
        context_experiment = response.context["experiment"]
        assert random_experiment.id == context_experiment.id

        url = reverse("animalv2:experiment_update", args=(random_experiment.id,))
        response = check_200(client, url)
