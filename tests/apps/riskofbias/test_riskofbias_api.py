import pytest
from django.core.urlresolvers import reverse
from django.test.client import Client

from hawc.apps.riskofbias.models import RiskOfBiasScore


@pytest.mark.django_db
def test_riskofbias_detail(db_keys):
    # check read-version of study api; including deeply nested scores and overridden objects
    client = Client()
    assert client.login(username="team@team.com", password="pw") is True

    url = reverse("study:api:study-detail", kwargs={"pk": db_keys.study_working})
    response = client.get(url)
    assert response.status_code == 200

    rob = response.json()["riskofbiases"]
    assert len(rob) == 3
    assert rob[2]["scores"][1]["is_default"] is True
    assert rob[2]["scores"][2]["is_default"] is False
    assert rob[2]["scores"][2]["overridden_objects"] == [
        {
            "id": 1,
            "score_id": 9,
            "content_type_name": "animal.endpoint",
            "object_id": 1,
            "object_name": "my outcome",
            "object_url": "/ani/endpoint/1/",
        }
    ]


@pytest.mark.django_db
def test_riskofbias_override_options(db_keys):
    # check read-version of study api; including deeply nested scores and overridden objects
    c = Client()
    assert c.login(username="team@team.com", password="pw") is True

    url = reverse("riskofbias:api:review-override-options", kwargs={"pk": db_keys.study_working})
    response = c.get(url)
    assert response.status_code == 200

    assert response.json() == {
        "animal.endpoint": [[1, "2 year bioassay → tester → my outcome", "/ani/endpoint/1/"]],
        "animal.animalgroup": [[1, "2 year bioassay → tester", "/ani/animal-group/1/"]],
        "epi.outcome": [],
        "epi.exposure": [],
        "epi.result": [],
    }


@pytest.mark.django_db
def test_riskofbias_delete_score(db_keys):
    c = Client()
    assert c.login(username="team@team.com", password="pw") is True

    # ensure you can delete a non-default score
    score = RiskOfBiasScore.objects.filter(is_default=False).first()
    url = (
        reverse("riskofbias:api:scores-detail", args=(score.id,))
        + f"?assessment_id={score.riskofbias.study.assessment_id}&ids={score.id}"
    )
    assert c.get(url).status_code == 200
    assert c.delete(url).status_code == 204
    assert c.get(url).status_code == 404

    # but cannot delete a default score
    score = RiskOfBiasScore.objects.filter(is_default=True).first()
    url = (
        reverse("riskofbias:api:scores-detail", args=(score.id,))
        + f"?assessment_id={score.riskofbias.study.assessment_id}&ids={score.id}"
    )
    assert c.get(url).status_code == 200
    assert c.delete(url).status_code == 403
    assert c.get(url).status_code == 200
