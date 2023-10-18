import json
from copy import deepcopy
from pathlib import Path

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from hawc.apps.myuser.models import HAWCUser
from hawc.apps.riskofbias.models import RiskOfBias, RiskOfBiasMetric, RiskOfBiasScore
from hawc.apps.study.models import Study

from ..test_utils import check_details_of_last_log_entry

DATA_ROOT = Path(__file__).parents[3] / "data/api"


@pytest.mark.django_db
class TestRiskOfBiasAssessmentViewSet:
    def test_full_export(self, rewrite_data_files: bool, db_keys):
        # permission check
        anon_client = APIClient()
        rev_client = APIClient()
        assert rev_client.login(username="reviewer@hawcproject.org", password="pw") is True
        tm_client = APIClient()
        assert tm_client.login(username="team@hawcproject.org", password="pw") is True

        url = reverse("riskofbias:api:assessment-full-export", args=(db_keys.assessment_working,))
        assert anon_client.get(url).status_code == 403
        assert rev_client.get(url).status_code == 403
        assert tm_client.get(url).status_code == 200

        fn = Path(DATA_ROOT / "api-rob-assessment-full-export.json")
        url = (
            reverse("riskofbias:api:assessment-full-export", args=(db_keys.assessment_final,))
            + "?format=json"
        )

        # check data
        resp = tm_client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        if rewrite_data_files:
            Path(fn).write_text(json.dumps(data, indent=2, sort_keys=True))
        assert data == json.loads(fn.read_text())

    def test_export(self, rewrite_data_files: bool, db_keys):
        # permission check
        anon_client = APIClient()
        rev_client = APIClient()
        assert rev_client.login(username="reviewer@hawcproject.org", password="pw") is True
        tm_client = APIClient()
        assert tm_client.login(username="team@hawcproject.org", password="pw") is True

        url = reverse("riskofbias:api:assessment-full-export", args=(db_keys.assessment_working,))
        assert anon_client.get(url).status_code == 403
        assert rev_client.get(url).status_code == 403
        assert tm_client.get(url).status_code == 200

        # data check
        fn = Path(DATA_ROOT / "api-rob-assessment-export.json")
        url = (
            reverse("riskofbias:api:assessment-export", args=(db_keys.assessment_final,))
            + "?format=json"
        )

        resp = anon_client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        if rewrite_data_files:
            Path(fn).write_text(json.dumps(data, indent=2, sort_keys=True))
        assert data == json.loads(fn.read_text())

    def test_PandasXlsxRenderer(self, db_keys):
        """
        Make sure that our pandas xlsx serializer effectively returns JSON when needed.

        We add this test to this viewset because it's related to a full ViewSet lifecycle and
        not just the logic in a Renderer; thus it's essentially an integration test for this
        renderer type; test was added based on security scan.
        """
        client = APIClient()

        url = (
            reverse("riskofbias:api:assessment-export", args=(db_keys.assessment_final,))
            + "?format=xlsx"
        )

        # the normal path worth via GET
        response = client.get(url)
        assert response.status_code == 200

        # an OPTIONS returns JSON
        response = client.options(url)
        assert response.status_code == 200
        expected_keys = {"name", "description", "renders", "parses"}
        assert set(json.loads(response.content).keys()) == expected_keys

        # a POST returns JSON and status_code
        response = client.post(url)
        assert response.status_code == 405
        assert json.loads(response.content) == {"detail": 'Method "POST" not allowed.'}

    def test_rob_bulk_copy(self, db_keys):
        client = APIClient()
        url = reverse("riskofbias:api:assessment-bulk-rob-copy")
        data = {
            "src_assessment_id": 1,
            "dst_assessment_id": 2,
            "src_dst_study_ids": [(1, 5)],
            "src_dst_metric_ids": [(1, 14), (2, 15)],
            "copy_mode": 1,
            "author_mode": 1,
        }

        # only pm and higher can perform this action
        assert client.login(username="team@hawcproject.org", password="pw") is True
        resp = client.post(url, data, format="json")
        assert resp.status_code == 403

        # valid request
        assert client.login(username="pm@hawcproject.org", password="pw") is True
        resp = client.post(url, data, format="json")
        assert resp.status_code == 200
        assert list(resp.data.keys()) == ["mapping"]

        # invalid request
        data["src_assessment_id"] = -1
        resp = client.post(url, data, format="json")
        assert resp.status_code == 400


@pytest.mark.django_db
def test_riskofbias_detail(db_keys):
    # check read-version of study api; including deeply nested scores and overridden objects
    client = APIClient()
    assert client.login(username="team@hawcproject.org", password="pw") is True

    # study detail
    url = reverse("study:api:study-detail", kwargs={"pk": db_keys.study_working})
    response = client.get(url)
    assert response.status_code == 200
    rob = response.json()["riskofbiases"]
    assert len(rob) == 1
    assert "author" not in rob[0]

    # study detail; all rob
    url = reverse("study:api:study-rob", args=(db_keys.study_working,))
    response = client.get(url)
    assert response.status_code == 200

    rob = response.json()
    assert len(rob) == 3
    assert "author" in rob[0]
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
    assert c.login(username="team@hawcproject.org", password="pw") is True

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
    assert c.login(username="team@hawcproject.org", password="pw") is True

    # ensure you can delete a non-default score
    assessment_id = 1  # editable assessment
    assessment_scores = RiskOfBiasScore.objects.filter(metric__domain__assessment_id=assessment_id)
    score = assessment_scores.filter(is_default=False).first()
    url = (
        reverse("riskofbias:api:scores-detail", args=(score.id,))
        + f"?assessment_id={assessment_id}&ids={score.id}"
    )
    assert c.get(url).status_code == 200
    assert c.delete(url).status_code == 204
    check_details_of_last_log_entry(score.id, "Deleted riskofbias.riskofbiasscore")
    assert c.get(url).status_code == 404

    # but cannot delete a default score
    score = assessment_scores.filter(is_default=True).first()
    url = (
        reverse("riskofbias:api:scores-detail", args=(score.id,))
        + f"?assessment_id={assessment_id}&ids={score.id}"
    )
    assert c.get(url).status_code == 200
    assert c.delete(url).status_code == 403
    assert c.get(url).status_code == 200


@pytest.mark.django_db
def test_riskofbias_post_overrides():
    c = APIClient()
    assert c.login(username="team@hawcproject.org", password="pw") is True

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
                bias_direction=score.bias_direction,
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
                bias_direction=0,
                score=dummy_score,
                notes="sample note",
            )
            for metric in metrics
        ],
    }
    return payload


@pytest.mark.django_db
def test_riskofbias_create():
    # check upload version of RoB api
    client = APIClient()
    assert client.login(username="team@hawcproject.org", password="pw") is True

    url = reverse("riskofbias:api:review-list")

    rev_author = HAWCUser.objects.get(email="reviewer@hawcproject.org")
    pm_author = HAWCUser.objects.get(email="pm@hawcproject.org")
    study = Study.objects.get(id=1)

    required_metrics = RiskOfBiasMetric.objects.get_required_metrics(study)
    first_valid_score = required_metrics[0].get_default_response()

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
    check_details_of_last_log_entry(resp.data["id"], "Created")

    # no scores submitted for a metric
    RiskOfBias.objects.all().delete()
    payload = build_upload_payload(study, pm_author, required_metrics, first_valid_score)
    payload["scores"].pop()
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 400
    assert b"No score for metric" in resp.content

    # metric scores submitted that are not required for the given study type
    extra_metrics = RiskOfBiasMetric.objects.filter(required_animal=False)
    new_metrics = required_metrics.union(extra_metrics)
    payload = build_upload_payload(study, pm_author, new_metrics, first_valid_score)
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 400
    extra_ids = ", ".join(map(str, [metric.id for metric in extra_metrics]))
    assert f"Metrics {extra_ids} were submitted but are not required for this study type" in str(
        resp.content
    )

    # no default score submitted for a metric
    RiskOfBias.objects.all().delete()
    payload = build_upload_payload(study, pm_author, required_metrics, first_valid_score)
    payload["scores"][0]["is_default"] = False
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 400
    assert b"No default score for metric" in resp.content

    # multiple default scores submitted for a metric
    payload = build_upload_payload(study, pm_author, required_metrics, first_valid_score)
    payload["scores"].append(payload["scores"][0])
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 400
    assert b"Multiple default scores for metric" in resp.content

    # demonstrate overridden objects with a unsupported content type
    RiskOfBias.objects.all().delete()
    payload = build_upload_payload(study, pm_author, required_metrics, first_valid_score)
    payload["scores"][0]["overridden_objects"] = [
        {"content_type_name": "animal.dosingregime", "object_id": 999}
    ]
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 400
    assert b"Invalid content type name" in resp.content

    # demonstrate overridden objects with a valid content type but a bad object_id
    RiskOfBias.objects.all().delete()
    payload = build_upload_payload(study, pm_author, required_metrics, first_valid_score)
    payload["scores"][0]["overridden_objects"] = [
        {"content_type_name": "animal.animalgroup", "object_id": 999}
    ]
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 400
    assert b"Invalid content object" in resp.content

    # demonstrate valid overridden objects
    RiskOfBias.objects.all().delete()
    payload = build_upload_payload(study, pm_author, required_metrics, first_valid_score)
    payload["scores"][0]["overridden_objects"] = [
        {"content_type_name": "animal.animalgroup", "object_id": 1}
    ]
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 201
    assert "created" in resp.data
    assert "scores" in resp.data and len(resp.data["scores"]) == 2
    check_details_of_last_log_entry(resp.data["id"], "Created")

    # demonstrate working bias override
    payload = build_upload_payload(study, pm_author, required_metrics, first_valid_score)
    payload["final"] = False
    payload["scores"][0]["bias_direction"] = 1
    resp = client.post(url, payload, format="json")
    assert resp.status_code == 201
    assert resp.json()["scores"][0]["bias_direction"] == 1


@pytest.mark.django_db
class TestBulkRobCleanupApis:
    """
    Make sure all the APIs we're using for the risk of bias score cleanup are working and return
    data as expected.
    """

    def test_study_types(self, db_keys):
        c = APIClient()
        assert c.login(username="team@hawcproject.org", password="pw") is True
        assessment_query = f"?assessment_id={db_keys.assessment_working}"
        url = reverse("study:api:study-types") + assessment_query

        resp = c.get(url, format="json")
        assert resp.status_code == 200
        assert set(resp.json()) == {"in_vitro", "bioassay", "epi_meta", "epi", "eco"}

    def test_metrics_list(self, db_keys):
        c = APIClient()
        assert c.login(username="team@hawcproject.org", password="pw") is True
        assessment_query = f"?assessment_id={db_keys.assessment_working}"

        url = reverse("riskofbias:api:metrics-list") + assessment_query
        resp = c.get(url, format="json")
        assert resp.status_code == 200
        assert (
            resp.json()[0].items()
            >= {
                "id": 1,
                "name": "example metric",
                "description": "<p>Is this a good study?</p>",
            }.items()
        )
        assert (
            resp.json()[1].items() >= {"id": 2, "name": "final domain", "description": ""}.items()
        )

    def test_rob_scores(self, db_keys):
        c = APIClient()
        assert c.login(username="team@hawcproject.org", password="pw") is True
        assessment_query = f"?assessment_id={db_keys.assessment_working}"

        # get metrics for score
        url = reverse("riskofbias:api:metrics-list") + assessment_query
        metrics = c.get(url, format="json").json()

        # get available rob scores for a metric
        detail_url = (
            reverse("riskofbias:api:scores-detail", args=(metrics[0]["id"],)) + assessment_query
        )
        resp = c.get(detail_url, format="json")
        assert resp.status_code == 200

        data = resp.json()
        assert data == {
            "id": 1,
            "score": 17,
            "is_default": True,
            "label": "",
            "bias_direction": 0,
            "notes": "<p>Content here.</p>",
            "overridden_objects": [],
            "riskofbias_id": 1,
            "metric_id": 1,
            "score_description": "Definitely low risk of bias",
            "score_shade": "#00CC00",
            "score_symbol": "++",
        }


@pytest.mark.django_db
class TestRobAssignmentApi:
    def test_create_individual(self):
        c = APIClient()
        url = reverse("riskofbias:api:review-create-v2")

        # permissions check
        assert c.login(username="team@hawcproject.org", password="pw") is True
        resp = c.post(url, dict(study=1, author=3, active=True, final=False))
        assert resp.status_code == 403

        assert c.login(username="pm@hawcproject.org", password="pw") is True

        # validation errors
        resp = c.post(url, dict(study=1, author=5, active=True, final=False))
        assert resp.status_code == 400
        assert resp.json() == {"author": ["Author cannot be assigned"]}

        # success
        resp = c.post(url, dict(study=1, author=3, active=True, final=False))
        assert resp.status_code == 201

    def test_create_final(self):
        c = APIClient()
        url = reverse("riskofbias:api:review-create-v2")

        assert c.login(username="pm@hawcproject.org", password="pw") is True
        existing_final = RiskOfBias.objects.get(study=1, active=True, final=True)
        assert existing_final.active is True

        # creating inactive final shouldn't change
        resp = c.post(url, dict(study=1, author=3, active=False, final=True))
        assert resp.status_code == 201
        existing_final.refresh_from_db()
        assert existing_final.active is True

        # creating active non-final shouldn't change
        resp = c.post(url, dict(study=1, author=3, active=True, final=False))
        assert resp.status_code == 201
        existing_final.refresh_from_db()
        assert existing_final.active is True

        # creating active final should change
        resp = c.post(url, dict(study=1, author=3, active=True, final=True))
        assert resp.status_code == 201
        existing_final.refresh_from_db()
        assert existing_final.active is False

    def test_update_individual(self):
        rob = RiskOfBias.objects.filter(study=1, active=True, final=False).first()
        c = APIClient()
        url = reverse("riskofbias:api:review-update-v2", args=(rob.id,))

        # permissions check
        assert c.login(username="team@hawcproject.org", password="pw") is True
        resp = c.patch(url, dict(active=False, author=3))
        assert resp.status_code == 403

        assert c.login(username="pm@hawcproject.org", password="pw") is True

        # validation errors
        resp = c.patch(url, dict(active=False, author=5))
        assert resp.status_code == 400
        assert resp.json() == {"author": ["Author cannot be assigned"]}

        # success
        resp = c.patch(url, dict(active=False, author=2))
        assert resp.status_code == 200

    def test_update_final(self):
        rob = RiskOfBias.objects.filter(study=1, active=True, final=True).first()
        c = APIClient()
        url = reverse("riskofbias:api:review-update-v2", args=(rob.id,))

        # permissions check
        assert c.login(username="team@hawcproject.org", password="pw") is True
        resp = c.patch(url, dict(active=False, author=3))
        assert resp.status_code == 403

        assert c.login(username="pm@hawcproject.org", password="pw") is True

        # validation errors
        resp = c.patch(url, dict(active=False, author=5))
        assert resp.status_code == 400
        assert resp.json() == {"author": ["Author cannot be assigned"]}

        # success
        resp = c.patch(url, dict(author=2, active=True))
        assert resp.status_code == 200
