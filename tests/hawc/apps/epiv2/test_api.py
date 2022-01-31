import json
from pathlib import Path
from django import db

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from rest_framework.test import APIClient

from hawc.apps.assessment.models import Assessment, Log
from hawc.apps.epiv2 import models


@pytest.mark.django_db
class TestDesignApi:
    def test_permissions(self, db_keys):
        url = reverse("epiv2:api:design-list")
        data = {
            "study": db_keys.study_working,
            "study_design": "CC",
            "source": "GP",
            "age_description": "10-15 yrs",
            "sex": "B",
            "race": "Not specified but likely primarily Asian",
            "summary": "Case-control study of asthma in children",
            "study_name": "Genetic and Biomarkers study for Childhood Asthma",
            "region": "northern Taiwan",
            "years": "2009-2010",
            "participant_n": 456,
            "age_profile": ["Children and adolescents <18 yrs"],
            "countries": ["TW"]
        }
        generic_perm_tester(url, data)

    
    def test_valid_requests(self, db_keys):
        url = reverse("epiv2:api:design-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        data = {
            "study": db_keys.study_working,
            "study_design": "CC",
            "source": "GP",
            "age_description": "10-15 yrs",
            "sex": "B",
            "race": "Not specified but likely primarily Asian",
            "summary": "test epidemiology study design",
            "study_name": "Genetic and Biomarkers study for Childhood Asthma",
            "region": "northern Taiwan",
            "years": "2009-2010",
            "participant_n": 456,
            "age_profile": ["Children and adolescents <18 yrs"],
            "countries": ["TW"]
        }

        just_created_design_id = None

        def design_lookup_test(resp):
            nonlocal just_created_design_id

            design_id = resp.json()["id"]
            design = models.Design.objects.get(id=design_id)
            assert design.source == "GP"
            assert design.summary == data["summary"]
            # Etc...

            if just_created_design_id is None:
                just_created_design_id = design_id

        def altered_design_test(resp):
            nonlocal just_created_design_id

            design_id = resp.json()["id"]
            design = models.Design.objects.get(id=design_id)
            assert design.summary == "updated"
            assert design_id == just_created_design_id

        def deleted_design_test(resp):
            nonlocal just_created_design_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.Design.objects.get(id=just_created_design_id)

        create_scenarios = (
            {
                "desc": "design create",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": data,
                "post_request_test": design_lookup_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        update_scenarios = (
            {
                "desc": "design update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"summary": "updated"},
                "method": "PATCH",
                "post_request_test": altered_design_test,
            },
        )
        url = f"{url}{just_created_design_id}/"
        generic_test_scenarios(client, url, update_scenarios)

        delete_scenarios = (
            {
                "desc": "design delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_design_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)


    def test_bad_requests(self, db_keys):
        url = reverse("epiv2:api:design-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        scenarios = (
            {
                "desc": "empty payload doesn't crash",
                "expected_code": 400,
                "expected_keys": {"study"},
                "data": {},
            },
            {
                "desc": "valid study id req'd",
                "expected_code": 400,
                "expected_keys": {"study"},
                "data": {"study": -1},
            },
        )
        generic_test_scenarios(client, url, scenarios)


def check_details_of_last_log_entry(obj_id: int, start_of_msg: str):
    """
    retrieve the latest log entry and check that the object_id/message look right.
    """
    log_entry = Log.objects.latest("id")
    assert log_entry.object_id == int(obj_id) and log_entry.message.startswith(start_of_msg)


def generic_test_scenarios(client, url, scenarios):
    for scenario in scenarios:
        method = scenario.get("method", "POST")
        if "data" in scenario:
            pass
        if method.upper() == "POST":
            response = client.post(url, scenario["data"], format="json")
        elif method.upper() == "PATCH":
            response = client.patch(url, scenario["data"], format="json")
        elif method.upper() == "DELETE":
            response = client.delete(url)
        else:
            return

        if "expected_code" in scenario:
            assert response.status_code == scenario["expected_code"]

        if "expected_keys" in scenario:
            assert (scenario["expected_keys"]).issubset((response.data.keys()))

        if "expected_content" in scenario:
            assert str(response.data).lower().find(scenario["expected_content"].lower()) != -1

        if "post_request_test" in scenario:
            scenario["post_request_test"](response)

        # make sure the audit/log table is getting updated while we're at it
        if response.status_code in [200, 201, 204]:  # successful create/update/delete:
            if method.upper() == "POST":
                check_details_of_last_log_entry(response.data["id"], "Created")
            elif method.upper() == "PATCH":
                check_details_of_last_log_entry(response.data["id"], "Updated")
            elif method.upper() == "DELETE":
                # get the id from the url, e.g. "/epi/api/study-population/2/"
                deleted_id = url.strip("/").split("/")[-1]
                check_details_of_last_log_entry(deleted_id, "Deleted")


def generic_perm_tester(url, data):
    # Reviewers shouldn't be able to create
    client = APIClient()
    assert client.login(username="reviewer@hawcproject.org", password="pw") is True
    response = client.post(url, data, format="json")
    assert response.status_code == 403

    # Public shouldn't be able to create
    client = APIClient()
    response = client.post(url, data, format="json")
    assert response.status_code == 403


def generic_get_any(model_class):
    return model_class.objects.all().first()