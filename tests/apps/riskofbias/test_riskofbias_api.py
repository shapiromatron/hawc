from copy import deepcopy

import pytest
from django.core.urlresolvers import reverse
from rest_framework.test import APIClient

from hawc.apps.myuser.models import HAWCUser
from hawc.apps.riskofbias.models import RiskOfBias, RiskOfBiasAssessment, RiskOfBiasMetric, RiskOfBiasScore
from hawc.apps.study.models import Study


@pytest.mark.django_db
def test_riskofbias_detail(db_keys):
    # check read-version of study api; including deeply nested scores and overridden objects
    client = APIClient()
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
    c = APIClient()
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
    c = APIClient()
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


@pytest.mark.django_db
def test_riskofbias_post_overrides():
    c = APIClient()
    assert c.login(username="team@team.com", password="pw") is True

    rob = RiskOfBias.objects.get(id=1)
    url = reverse("riskofbias:api:review-detail", args=(rob.id,))
    payload = {
        "id": rob.id,
        "scores": [
            dict(
                id=score.id,
                label=score.label,
                notes="<p>my new notes!</p>",
                score=score.score,
                overridden_objects=[],
            )
            for score in rob.scores.all()
        ],
    }

    # setup; check initial data is different than patch
    resp = c.get(url, format="json")
    assert resp.status_code == 200
    assert b"<p>my new notes!</p>" not in resp.content

    # demonstrate successful patch and new data reflects patch
    resp = c.patch(url, payload, format="json")
    assert resp.status_code == 200
    assert resp.data["id"] == payload["id"]
    assert len(resp.data["scores"][0]["overridden_objects"]) == 0
    assert b"<p>my new notes!</p>" in resp.content

    # demonstrate successful path with override
    new_payload = deepcopy(payload)
    new_payload["scores"][0]["overridden_objects"] = [
        {"content_type_name": "animal.animalgroup", "object_id": 1}
    ]
    resp = c.patch(url, new_payload, format="json")
    assert resp.status_code == 200
    assert len(resp.data["scores"][0]["overridden_objects"]) == 1
    assert resp.data["scores"][0]["overridden_objects"][0]["object_url"] == "/ani/animal-group/1/"

    # demonstrate invalid score id from another assessment
    new_payload = deepcopy(payload)
    new_payload["scores"][0]["id"] = RiskOfBias.objects.get(id=2).scores.first().id
    resp = c.patch(url, new_payload, format="json")
    assert resp.status_code == 400
    assert resp.data == {"non_field_errors": ["Cannot update; scores to not match instances"]}

    # demonstrate invalid override #1
    new_payload = deepcopy(payload)
    new_payload["scores"][0]["overridden_objects"] = [
        {"content_type_name": "animal.animalgroup", "object_id": 2}
    ]
    resp = c.patch(url, new_payload, format="json")
    assert resp.status_code == 400
    assert resp.data == {"non_field_errors": ["Invalid content object: animal.animalgroup: 2"]}

    # demonstrate invalid override #2
    new_payload = deepcopy(payload)
    new_payload["scores"][0]["overridden_objects"] = [
        {"content_type_name": "invalid.contenttype", "object_id": 1}
    ]
    resp = c.patch(url, new_payload, format="json")
    assert resp.status_code == 400
    assert resp.data == {"non_field_errors": ["Invalid content type name: invalid.contenttype"]}

    # ensure we can delete
    assert c.delete(url).status_code == 204

def build_upload_payload(study, author, metrics, dummy_score):
    payload = {
        "study_id": study.id if study is not None else -1,
        "author_id": author.id if author is not None else -1,
        "active": True,
        "final": True,
        "scores": [
            dict(
                metric_id=metric.id,
                is_default=True,
                label="",
                score=dummy_score,
                notes="sample note"
            )
            for metric in metrics
        ]
    }
    return payload

@pytest.mark.django_db
def test_riskofbias_create():
    # check upload version of RoB api
    client = APIClient()
    assert client.login(username="team@team.com", password="pw") is True

    url = reverse("riskofbias:api:review-list")

    rev_author = HAWCUser.objects.get(email="rev@rev.com")
    pm_author = HAWCUser.objects.get(email="pm@pm.com")
    study = Study.objects.get(id=1)

    required_metrics = RiskOfBiasMetric.objects.get_required_metrics(study.assessment, study)
    first_valid_score = RiskOfBiasAssessment().get_rob_response_values()[0]
    
    # failed uploading for a study that already has an active & final RoB
    payload = build_upload_payload(study, pm_author, required_metrics, first_valid_score)
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 400
    assert b"already has an active" in resp.content

    # bad score value
    payload = build_upload_payload(study, pm_author, required_metrics, -999)
    payload["scores"][0]["score"] *= -1
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 400
    assert b"is not a valid choice" in resp.content

    # author without permissions for the study/assessment
    payload = build_upload_payload(study, rev_author, required_metrics, first_valid_score)
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 400
    assert b"has invalid permissions" in resp.content

    # invalid study_id
    payload = build_upload_payload(None, pm_author, required_metrics, first_valid_score)
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 400
    assert b"Invalid study_id" in resp.content

    # invalid author_id
    payload = build_upload_payload(study, None, required_metrics, first_valid_score)
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 400
    assert b"Invalid author_id" in resp.content

    # delete existing RoBs so we can insert (study already has active/final)
    RiskOfBias.objects.all().delete()
    payload = build_upload_payload(study, pm_author, required_metrics, first_valid_score)
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 201
    assert "created" in resp.data
    assert "scores" in resp.data and len(resp.data["scores"]) == 2
