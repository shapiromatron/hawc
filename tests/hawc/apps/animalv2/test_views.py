import pytest
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.animalv2 import models

from ..test_utils import check_200, check_403, get_client, get_first


@pytest.mark.django_db
def test_get_200(db_keys):
    client = get_client("team")
    urls = [
        reverse("animalv2:studylevelvalues", args=(db_keys.study_working,)),
        reverse("animalv2:observation-list", args=(1,)),
    ]
    for url in urls:
        check_200(client, url)


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


@pytest.mark.django_db
class TestObservationViewSet:
    def test_crud(self):
        c = get_client("admin", htmx=True)

        # create (post)
        url = (
            reverse("animalv2:observation-htmx", args=(1, "tested_status", "create"))
            + "?endpoint=7002"
        )
        response = c.post(
            url,
            {
                "7002-tested": "True",
            },
            follow=True,
        )
        assert assertTemplateUsed("animalv2/fragments/observation_form.html")
        assert response.status_code == 200
