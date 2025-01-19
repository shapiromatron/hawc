import pytest
from django.urls import reverse

from hawc.apps.animalv2 import models

from ..test_utils import check_200, check_403, get_client, get_first


@pytest.mark.django_db
def test_get_200(db_keys):
    client = get_client("team")
    urls = [
        reverse("animalv2:studylevelvalues", args=(db_keys.study_working,)),
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
