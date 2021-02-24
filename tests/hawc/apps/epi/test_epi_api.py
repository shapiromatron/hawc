import json
from pathlib import Path

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework.test import APIClient

from hawc.apps.assessment.models import Assessment
from hawc.apps.epi import models

DATA_ROOT = Path(__file__).parents[3] / "data/api"


@pytest.mark.django_db
class TestEpiAssessmentViewset:
    def _test_flat_export(self, rewrite_data_files: bool, fn: str, url: str):

        client = APIClient()
        assert client.login(username="reviewer@hawcproject.org", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        path = Path(DATA_ROOT / fn)
        data = resp.json()

        if rewrite_data_files:
            path.write_text(json.dumps(data, indent=2))

        assert data == json.loads(path.read_text())

    def test_permissions(self, db_keys):
        rev_client = APIClient()
        assert rev_client.login(username="reviewer@hawcproject.org", password="pw") is True
        anon_client = APIClient()

        urls = [
            reverse("epi:api:assessment-export", args=(db_keys.assessment_working,)),
            reverse("epi:api:assessment-study-heatmap", args=(db_keys.assessment_working,)),
            reverse("epi:api:assessment-result-heatmap", args=(db_keys.assessment_working,)),
        ]
        for url in urls:
            assert anon_client.get(url).status_code == 403
            assert rev_client.get(url).status_code == 200

    def test_full_export(self, rewrite_data_files: bool, db_keys):
        fn = "api-epi-assessment-export.json"
        url = reverse(f"epi:api:assessment-export", args=(db_keys.assessment_final,))
        self._test_flat_export(rewrite_data_files, fn, url)

    def test_study_heatmap(self, rewrite_data_files: bool, db_keys):
        # published
        fn = "api-epi-assessment-study-heatmap-unpublished-False.json"
        url = reverse(f"epi:api:assessment-study-heatmap", args=(db_keys.assessment_final,))
        self._test_flat_export(rewrite_data_files, fn, url)

        # unpublished
        fn = "api-epi-assessment-study-heatmap-unpublished-True.json"
        url = (
            reverse(f"epi:api:assessment-study-heatmap", args=(db_keys.assessment_final,))
            + "?format=json&unpublished=true"
        )
        self._test_flat_export(rewrite_data_files, fn, url)

    def test_result_heatmap(self, rewrite_data_files: bool, db_keys):
        # published
        fn = "api-epi-assessment-result-heatmap-unpublished-False.json"
        url = reverse(f"epi:api:assessment-result-heatmap", args=(db_keys.assessment_final,))
        self._test_flat_export(rewrite_data_files, fn, url)

        # unpublished
        fn = "api-epi-assessment-result-heatmap-unpublished-True.json"
        url = (
            reverse(f"epi:api:assessment-result-heatmap", args=(db_keys.assessment_final,))
            + "?format=json&unpublished=true"
        )
        self._test_flat_export(rewrite_data_files, fn, url)


@pytest.mark.django_db
class TestStudyPopulationApi:
    def test_permissions(self, db_keys):
        url = reverse("epi:api:study-population-list")
        data = {
            "study": db_keys.study_working,
            "name": "study pop name",
            "design": "CO",
            "age_profile": "test profile",
            "source": "test source",
            "countries": ["JP"],
            "region": "test region",
            "state": "test state",
            "eligible_n": 3,
            "invited_n": 2,
            "participant_n": 1,
            "comments": "test comments",
        }
        generic_perm_tester(url, data)

    def test_bad_requests(self, db_keys):
        url = reverse("epi:api:study-population-list")
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
            {
                "desc": "countries/design/name req'd",
                "expected_code": 400,
                "expected_keys": {"countries", "design", "name"},
                "data": {"study": db_keys.study_working},
            },
            {
                "desc": "valid country req'd",
                "expected_code": 400,
                "expected_keys": {"countries"},
                "data": {"study": db_keys.study_working, "countries": ["ZZZ"]},
            },
            {
                "desc": "valid design req'd",
                "expected_code": 400,
                "expected_keys": {"design"},
                "data": {"study": db_keys.study_working, "design": "bad_val"},
            },
            {
                "desc": "obey data types",
                "expected_code": 400,
                "expected_keys": {"eligible_n", "invited_n", "participant_n"},
                "data": {
                    "study": db_keys.study_working,
                    "eligible_n": "not_numeric",
                    "invited_n": {},
                    "participant_n": False,
                },
            },
        )

        generic_test_scenarios(client, url, scenarios)

    def test_valid_requests(self, db_keys):
        url = reverse("epi:api:study-population-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        # make some test criteria
        assessment = Assessment.objects.get(id=db_keys.assessment_working)
        criteria1 = models.Criteria(assessment=assessment, description="dummy 1")
        criteria1.save()

        criteria2 = models.Criteria(assessment=assessment, description="dummy 2")
        criteria2.save()

        base_data = {
            "study": db_keys.study_working,
            "name": "study pop name",
            "design": "CO",
            "age_profile": "test profile",
            "source": "test source",
            "countries": ["JP"],
            "region": "test region",
            "state": "test state",
            "eligible_n": 3,
            "invited_n": 2,
            "participant_n": 1,
            "comments": "test comments",
        }

        just_created_study_id = None

        def study_pop_lookup_test(resp):
            nonlocal just_created_study_id

            study_pop_id = resp.json()["id"]
            study_pop = models.StudyPopulation.objects.get(id=study_pop_id)
            assert study_pop.design == "CO"
            assert study_pop.name == base_data["name"]
            # etc...

            if just_created_study_id is None:
                just_created_study_id = study_pop_id

        def study_pop_lookup_test_with_criteria(resp):
            study_pop_id = resp.json()["id"]
            study_pop = models.StudyPopulation.objects.get(id=study_pop_id)

            found_c1 = False
            found_c2 = False
            found_c3 = False
            for c in study_pop.criteria.all():
                if c.id == criteria1.id:
                    found_c1 = True
                elif c.id == criteria2.id:
                    found_c2 = True
                elif c.description == "on the fly":
                    found_c3 = True

            assert found_c1 is True and found_c2 is True and found_c3 is True

        def altered_study_pop_test(resp):
            nonlocal just_created_study_id

            study_pop_id = resp.json()["id"]
            study_pop = models.StudyPopulation.objects.get(id=study_pop_id)
            assert study_pop.name == "updated"
            assert study_pop_id == just_created_study_id

        def deleted_study_pop_test(resp):
            nonlocal just_created_study_id

            assert resp.data is None
            try:
                study_pop_that_should_not_exist = models.StudyPopulation.objects.get(
                    id=just_created_study_id
                )
                assert study_pop_that_should_not_exist is None
            except ObjectDoesNotExist:
                # this is CORRECT behavior - we WANT the object to not exist
                pass

        named_design_data = base_data
        named_design_data["design"] = "cohort"

        # You can supply criteria by either id or name; and if by name it will be created on-the-fly as needed.
        criteria_data = base_data
        criteria_data["inclusion_criteria"] = [
            criteria1.id,  # existing by id
            criteria2.description,  # existing by name
            "on the fly",  # brand new
        ]

        create_scenarios = (
            {
                "desc": "basic studypop creation",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": base_data,
                "post_request_test": study_pop_lookup_test,
            },
            {
                "desc": "named design studypop creation",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": named_design_data,
                "post_request_test": study_pop_lookup_test,
            },
            {
                "desc": "criteria variety",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": criteria_data,
                "post_request_test": study_pop_lookup_test_with_criteria,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        url = f"{url}{just_created_study_id}/"
        update_scenarios = (
            {
                "desc": "basic studypop update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"name": "updated"},
                "method": "PATCH",
                "post_request_test": altered_study_pop_test,
            },
        )
        generic_test_scenarios(client, url, update_scenarios)

        delete_scenarios = (
            {
                "desc": "delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_study_pop_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)


@pytest.mark.django_db
class TestCriteriaApi:
    def test_permissions(self, db_keys):
        url = reverse("epi:api:criteria-list")
        data = {"assessment": db_keys.assessment_working, "description": "test criteria"}
        generic_perm_tester(url, data)

    def test_bad_requests(self, db_keys):
        url = reverse("epi:api:criteria-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        scenarios = (
            {
                "desc": "empty payload doesn't crash",
                "expected_code": 400,
                "expected_keys": {"description", "assessment"},
                "data": {},
            },
            {
                "desc": "assessment must be a valid assessment id",
                "expected_code": 400,
                "expected_keys": {"assessment"},
                "data": {"description": "this is ok", "assessment": 999},
            },
            {
                "desc": "description must be a string",
                "expected_code": 400,
                "expected_keys": {"description"},
                "data": {"description": {}, "assessment": db_keys.assessment_working},
            },
        )

        generic_test_scenarios(client, url, scenarios)

    def test_valid_requests(self, db_keys):
        url = reverse("epi:api:criteria-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        base_data = {"assessment": db_keys.assessment_working, "description": "initial description"}

        just_created_criteria_id = None

        def criteria_lookup_test(resp):
            nonlocal just_created_criteria_id

            criteria_id = resp.json()["id"]
            criteria = models.Criteria.objects.get(id=criteria_id)
            assert criteria.description == base_data["description"]

            if just_created_criteria_id is None:
                just_created_criteria_id = criteria_id

        def second_creation_test(resp):
            nonlocal just_created_criteria_id

            criteria_id = resp.json()["id"]
            criteria = models.Criteria.objects.get(id=criteria_id)
            assert criteria.description == base_data["description"]
            assert criteria.id == just_created_criteria_id

        def altered_criteria_test(resp):
            nonlocal just_created_criteria_id

            criteria_id = resp.json()["id"]
            criteria = models.Criteria.objects.get(id=criteria_id)
            assert criteria.description == "updated"
            assert criteria_id == just_created_criteria_id

        def deleted_criteria_test(resp):
            nonlocal just_created_criteria_id

            assert resp.data is None
            try:
                criteria_that_should_not_exist = models.Criteria.objects.get(
                    id=just_created_criteria_id
                )
                assert criteria_that_should_not_exist is None
            except ObjectDoesNotExist:
                # this is CORRECT behavior - we WANT the object to not exist
                pass

        create_scenarios = (
            {
                "desc": "basic criteria creation",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": base_data,
                "post_request_test": criteria_lookup_test,
            },
            {
                "desc": "fetch - not create - criteria by name",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": base_data,
                "post_request_test": second_creation_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        url = f"{url}{just_created_criteria_id}/"
        update_scenarios = (
            {
                "desc": "basic criteria update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"description": "updated"},
                "method": "PATCH",
                "post_request_test": altered_criteria_test,
            },
        )
        generic_test_scenarios(client, url, update_scenarios)

        delete_scenarios = (
            {
                "desc": "delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_criteria_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)


@pytest.mark.django_db
class TestOutcomeApi:
    def test_permissions(self, db_keys):
        url = reverse("epi:api:outcome-list")
        data = {
            "name": "test outcome",
            "assessment": db_keys.assessment_working,
            "study_population": 1,
            "diagnostic": 0,
            "diagnostic_description": "dd",
        }
        generic_perm_tester(url, data)

    def test_bad_requests(self, db_keys):
        url = reverse("epi:api:outcome-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        scenarios = (
            {
                "desc": "empty payload doesn't crash",
                "expected_code": 400,
                "expected_keys": {"name", "diagnostic", "diagnostic_description"},
                "data": {},
            },
            {
                "desc": "assessment must be a valid assessment id",
                "expected_code": 400,
                "expected_keys": {"assessment"},
                "data": {"name": "this is ok", "assessment": 999},
            },
            {
                "desc": "diagnostic cannot be invalid id",
                "expected_code": 400,
                "expected_keys": {"diagnostic"},
                "data": {"name": "this is ok", "diagnostic": -1},
            },
            {
                "desc": "diagnostic cannot be invalid label",
                "expected_code": 400,
                "expected_keys": {"diagnostic"},
                "data": {"name": "this is ok", "diagnostic": "NOT questionnaire"},
            },
        )

        generic_test_scenarios(client, url, scenarios)

    def test_valid_requests(self, db_keys):
        url = reverse("epi:api:outcome-list")
        client = APIClient()
        # assert client.login(username="team@hawcproject.org", password="pw") is True
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        study_pops = models.StudyPopulation.objects.all()
        study_pop = None
        for sp in study_pops:
            study_pop = sp
            break
        # print(f"FOUND STUDY POP {study_pop} WHCHIS IN ASSESSMENT {study_pop.get_assessment().id}")

        diagnostic = models.Outcome.DIAGNOSTIC_CHOICES[0]
        diagnostic_code = diagnostic[0]
        diagnostic_name = diagnostic[1]

        base_data = {
            "name": "test outcome",
            "system": "blood",
            "assessment": study_pop.get_assessment().id,
            "diagnostic_description": "test diag desc",
            "diagnostic": diagnostic_code,
            "outcome_n": 100,
            "study_population": study_pop.id,
            "age_of_measurement": "test age",
            "summary": "test summary",
            "effect": "test effect",
            "effect_subtype": "test subtype",
        }

        diagname_data = base_data
        diagname_data["diagnostic"] = diagnostic_name.upper()

        just_created_outcome_id = None

        def outcome_lookup_test(resp):
            nonlocal just_created_outcome_id

            outcome_id = resp.json()["id"]
            outcome = models.Outcome.objects.get(id=outcome_id)
            assert outcome.name == base_data["name"]

            if just_created_outcome_id is None:
                just_created_outcome_id = outcome_id

        def altered_outcome_test(resp):
            nonlocal just_created_outcome_id

            outcome_id = resp.json()["id"]
            outcome = models.Outcome.objects.get(id=outcome_id)
            assert outcome.name == "updated"
            assert outcome_id == just_created_outcome_id

        def deleted_outcome_test(resp):
            nonlocal just_created_outcome_id

            assert resp.data is None
            try:
                outcome_that_should_not_exist = models.Outcome.objects.get(
                    id=just_created_outcome_id
                )
                assert outcome_that_should_not_exist is None
            except ObjectDoesNotExist:
                # this is CORRECT behavior - we WANT the object to not exist
                pass

        create_scenarios = (
            {
                "desc": "basic outcome creation",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": base_data,
                "post_request_test": outcome_lookup_test,
            },
            {
                "desc": "creation with diagnostic name",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": diagname_data,
                "post_request_test": outcome_lookup_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        url = f"{url}{just_created_outcome_id}/"
        update_scenarios = (
            {
                "desc": "basic outcome update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"name": "updated"},
                "method": "PATCH",
                "post_request_test": altered_outcome_test,
            },
        )
        generic_test_scenarios(client, url, update_scenarios)

        delete_scenarios = (
            {
                "desc": "delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_outcome_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)


def generic_test_scenarios(client, url, scenarios):
    print(f">>>>> testing scenarios against '{url}'...")
    for scenario in scenarios:
        print(f">>>>> testing '{scenario['desc']}'...")
        method = scenario.get("method", "POST")
        if "data" in scenario:
            # print(f">>>>> will {method} data: {scenario['data']}")
            pass
        if method.upper() == "POST":
            response = client.post(url, scenario["data"], format="json")
        elif method.upper() == "PATCH":
            response = client.patch(url, scenario["data"], format="json")
        elif method.upper() == "DELETE":
            response = client.delete(url)
        else:
            return

        print(f">>>>> {method} request came back wth {response.status_code} / {response.data}")
        if "expected_code" in scenario:
            assert response.status_code == scenario["expected_code"]

        if "expected_keys" in scenario:
            assert (scenario["expected_keys"]).issubset((response.data.keys()))

        if "post_request_test" in scenario:
            scenario["post_request_test"](response)


def generic_perm_tester(url, data):
    print(f">>>>> generic perm test on {url}")
    # reviewers shouldn't be able to create
    client = APIClient()
    assert client.login(username="reviewer@hawcproject.org", password="pw") is True
    response = client.post(url, data, format="json")
    assert response.status_code == 403

    # public shouldn't be able to create
    client = APIClient()
    response = client.post(url, data, format="json")
    assert response.status_code == 403
