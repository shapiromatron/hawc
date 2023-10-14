import json
from pathlib import Path

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from rest_framework.test import APIClient

from hawc.apps.assessment.models import Assessment, DoseUnits
from hawc.apps.epi import constants, models

from ..test_utils import check_details_of_last_log_entry

DATA_ROOT = Path(__file__).parents[3] / "data/api"


@pytest.mark.django_db
class TestEpiAssessmentViewSet:
    def _test_flat_export(self, rewrite_data_files: bool, fn: str, url: str):
        client = APIClient()
        assert client.login(username="reviewer@hawcproject.org", password="pw") is True
        resp = client.get(url)
        assert resp.status_code == 200

        path = Path(DATA_ROOT / fn)
        data = resp.json()

        if rewrite_data_files:
            path.write_text(json.dumps(data, indent=2, sort_keys=True))

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
        url = reverse("epi:api:assessment-export", args=(db_keys.assessment_final,))
        self._test_flat_export(rewrite_data_files, fn, url)

    def test_study_heatmap(self, rewrite_data_files: bool, db_keys):
        # published
        fn = "api-epi-assessment-study-heatmap-unpublished-False.json"
        url = reverse("epi:api:assessment-study-heatmap", args=(db_keys.assessment_final,))
        self._test_flat_export(rewrite_data_files, fn, url)

        # unpublished
        fn = "api-epi-assessment-study-heatmap-unpublished-True.json"
        url = (
            reverse("epi:api:assessment-study-heatmap", args=(db_keys.assessment_final,))
            + "?format=json&unpublished=true"
        )
        self._test_flat_export(rewrite_data_files, fn, url)

    def test_result_heatmap(self, rewrite_data_files: bool, db_keys):
        # published
        fn = "api-epi-assessment-result-heatmap-unpublished-False.json"
        url = reverse("epi:api:assessment-result-heatmap", args=(db_keys.assessment_final,))
        self._test_flat_export(rewrite_data_files, fn, url)

        # unpublished
        fn = "api-epi-assessment-result-heatmap-unpublished-True.json"
        url = (
            reverse("epi:api:assessment-result-heatmap", args=(db_keys.assessment_final,))
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

        # Make some test criteria
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

        just_created_study_pop_id = None

        def study_pop_lookup_test(resp):
            nonlocal just_created_study_pop_id

            study_pop_id = resp.json()["id"]
            study_pop = models.StudyPopulation.objects.get(id=study_pop_id)
            assert study_pop.design == "CO"
            assert study_pop.name == base_data["name"]
            # Etc...

            if just_created_study_pop_id is None:
                just_created_study_pop_id = study_pop_id

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
            nonlocal just_created_study_pop_id

            study_pop_id = resp.json()["id"]
            study_pop = models.StudyPopulation.objects.get(id=study_pop_id)
            assert study_pop.name == "updated"
            assert study_pop_id == just_created_study_pop_id

        def deleted_study_pop_test(resp):
            nonlocal just_created_study_pop_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.StudyPopulation.objects.get(id=just_created_study_pop_id)

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

        url = f"{url}{just_created_study_pop_id}/"
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
                "desc": "study pop delete",
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

            with pytest.raises(ObjectDoesNotExist):
                models.Criteria.objects.get(id=just_created_criteria_id)

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
                "desc": "criteria delete",
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
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        study_pops = models.StudyPopulation.objects.all()
        study_pop = None
        for sp in study_pops:
            study_pop = sp
            break

        diagnostic = constants.Diagnostic.NR
        diagnostic_code = diagnostic.value
        diagnostic_name = diagnostic.label

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

            with pytest.raises(ObjectDoesNotExist):
                models.Outcome.objects.get(id=just_created_outcome_id)

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
                "desc": "outcome delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_outcome_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)


@pytest.mark.django_db
class TestResultApi:
    def get_upload_data(self, overrides=None):
        outcome = generic_get_any(models.Outcome)
        comp_set = generic_get_any(models.ComparisonSet)
        result_metric = generic_get_any(models.ResultMetric)

        data = {
            "name": "result name",
            "dose_response": "monotonic",
            "metric": result_metric.id,
            "statistical_power": 2,
            "outcome": outcome.id,
            "estimate_type": "point",
            "variance_type": 4,
            "comparison_set": comp_set.id,
            "metric_description": "test met desc",
            "data_location": "test data loc",
            "population_description": "test pop desc",
            "dose_response_details": "test dose response details",
            "prevalence_incidence": "test prevalence incidence",
            "statistical_power_details": "test stat power details",
            "statistical_test_results": "test stat test results",
            "trend_test": "test trend test",
            "ci_units": 0.5,
            "factors_applied": [],
            "factors_considered": [],
            "comments": "test comments",
        }

        if overrides is not None:
            data.update(overrides)

        return data

    def test_permissions(self, db_keys):
        url = reverse("epi:api:result-list")
        generic_perm_tester(url, self.get_upload_data())

    def test_bad_requests(self, db_keys):
        url = reverse("epi:api:result-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        scenarios = (
            {"desc": "empty payload doesn't crash", "expected_code": 400, "data": {}},
            {
                "desc": "outcome must be valid",
                "expected_code": 400,
                "expected_keys": {"outcome"},
                "data": self.get_upload_data({"outcome": 999}),
            },
            {
                "desc": "metric/comparison_Set must be valid",
                "expected_code": 400,
                "expected_keys": {"metric", "comparison_set"},
                "data": self.get_upload_data({"metric": 999, "comparison_set": 999}),
            },
            {
                "desc": "factors_applied / considered cannot have invalid id's",
                "expected_code": 400,
                "data": self.get_upload_data(
                    {"factors_applied": [999], "factors_considered": [999]}
                ),
            },
            {
                "desc": "estimate/variance type need valid values",
                "expected_code": 400,
                "expected_keys": {"estimate_type", "variance_type"},
                "data": self.get_upload_data({"estimate_type": 999, "variance_type": "bad_value"}),
            },
            {
                "desc": "expect numeric types",
                "expected_code": 400,
                "expected_keys": {"ci_units"},
                "data": self.get_upload_data({"ci_units": "bad val"}),
            },
        )

        generic_test_scenarios(client, url, scenarios)

    def test_valid_requests(self, db_keys):
        url = reverse("epi:api:result-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        adj_factor = generic_get_any(models.AdjustmentFactor)

        just_created_result_id = None

        base_data = self.get_upload_data()

        def result_lookup_test(resp):
            nonlocal just_created_result_id

            result_id = resp.json()["id"]
            result = models.Result.objects.get(id=result_id)
            assert result.name == base_data["name"]

            if just_created_result_id is None:
                just_created_result_id = result_id

        def result_lookup_test_with_factors(resp):
            nonlocal just_created_result_id

            result_id = resp.json()["id"]
            result = models.Result.objects.get(id=result_id)
            assert result.name == base_data["name"]

            found_existing_by_id = False
            found_existing_by_description = False
            found_new_one = False
            for af in result.factors_applied:
                if af.id == adj_factor.id:
                    found_existing_by_description = True
                elif af.description == "on the fly":
                    found_new_one = True

            for af in result.factors_considered:
                if af.id == adj_factor.id:
                    found_existing_by_id = True

            assert (
                found_existing_by_id is True
                and found_existing_by_description is True
                and found_new_one is True
            )

        def altered_result_test(resp):
            nonlocal just_created_result_id

            result_id = resp.json()["id"]
            result = models.Result.objects.get(id=result_id)
            assert result.name == "updated"
            assert result_id == just_created_result_id

        def deleted_result_test(resp):
            nonlocal just_created_result_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.Result.objects.get(id=just_created_result_id)

        create_scenarios = (
            {
                "desc": "basic result creation",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data(),
                "post_request_test": result_lookup_test,
            },
            {
                "desc": "create with numeric est. type and named variance type",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data({"estimate_type": 1, "variance_type": "sd"}),
                "post_request_test": result_lookup_test,
            },
            {
                "desc": "add some adjustment factors",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data(
                    {
                        "factors_applied": [adj_factor.description, "on the fly"],
                        "factors_considered": [adj_factor.id],
                    }
                ),
                "post_request_test": result_lookup_test_with_factors,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        url = f"{url}{just_created_result_id}/"
        update_scenarios = (
            {
                "desc": "basic result update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"name": "updated"},
                "method": "PATCH",
                "post_request_test": altered_result_test,
            },
        )
        generic_test_scenarios(client, url, update_scenarios)

        delete_scenarios = (
            {
                "desc": "result delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_result_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)


@pytest.mark.django_db
class TestGroupResultApi:
    def get_upload_data(self, overrides=None):
        group = generic_get_any(models.Group)
        result = generic_get_any(models.Result)

        data = {
            "n": 50,
            "main_finding_support": constants.MainFinding.I,
            "p_value_qualifier": constants.PValueQualifier.NS,
            "p_value": 0.5,
            "group": group.id,
            "result": result.id,
            "estimate": 1,
            "variance": 2,
            "lower_ci": 3,
            "upper_ci": 4,
            "lower_range": 5,
            "upper_range": 6,
            "is_main_finding": False,
        }

        if overrides is not None:
            data.update(overrides)

        return data

    def test_permissions(self, db_keys):
        url = reverse("epi:api:group-result-list")
        generic_perm_tester(url, self.get_upload_data())

    def test_bad_requests(self, db_keys):
        url = reverse("epi:api:group-result-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        scenarios = (
            {"desc": "empty payload doesn't crash", "expected_code": 400, "data": {}},
            {
                "desc": "main_finding_support must be valid",
                "expected_code": 400,
                "expected_keys": {"main_finding_support"},
                "data": self.get_upload_data({"main_finding_support": "badval"}),
            },
            {
                "desc": "p_value_qualifier must be valid",
                "expected_code": 400,
                "expected_keys": {"p_value_qualifier"},
                "data": self.get_upload_data({"p_value_qualifier": "badval"}),
            },
            {
                "desc": "group/result must be valid",
                "expected_code": 400,
                "expected_keys": {"group", "result"},
                "data": self.get_upload_data({"group": 999, "result": 999}),
            },
            {
                "desc": "expect numeric types",
                "expected_code": 400,
                "expected_keys": {"lower_ci", "upper_range"},
                "data": self.get_upload_data({"lower_ci": "bad val", "upper_range": "xxx"}),
            },
        )

        generic_test_scenarios(client, url, scenarios)

    def test_valid_requests(self, db_keys):
        url = reverse("epi:api:group-result-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        just_created_groupresult_id = None

        base_data = self.get_upload_data()

        def groupresult_lookup_test(resp):
            nonlocal just_created_groupresult_id

            groupresult_id = resp.json()["id"]
            groupresult = models.GroupResult.objects.get(id=groupresult_id)
            assert groupresult.n == base_data["n"]

            if just_created_groupresult_id is None:
                just_created_groupresult_id = groupresult_id

        def altered_groupresult_test(resp):
            nonlocal just_created_groupresult_id

            groupresult_id = resp.json()["id"]
            groupresult = models.GroupResult.objects.get(id=groupresult_id)
            assert groupresult.n == 51
            assert groupresult_id == just_created_groupresult_id

        def deleted_groupresult_test(resp):
            nonlocal just_created_groupresult_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.GroupResult.objects.get(id=just_created_groupresult_id)

        create_scenarios = (
            {
                "desc": "basic groupresult creation",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data(),
                "post_request_test": groupresult_lookup_test,
            },
            {
                "desc": "create with named main_finding",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data(
                    {"main_finding_support": constants.MainFinding.I.label}
                ),
                "post_request_test": groupresult_lookup_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        url = f"{url}{just_created_groupresult_id}/"
        update_scenarios = (
            {
                "desc": "basic groupresult update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"n": 51},
                "method": "PATCH",
                "post_request_test": altered_groupresult_test,
            },
        )
        generic_test_scenarios(client, url, update_scenarios)

        delete_scenarios = (
            {
                "desc": "groupresult delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_groupresult_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)


@pytest.mark.django_db
class TestComparisonSetApi:
    def get_upload_data(self, overrides=None):
        exposure = generic_get_any(models.Exposure)
        study_pop = generic_get_any(models.StudyPopulation)

        data = {
            "name": "comparison set name",
            "description": "test description",
            "exposure": exposure.id,
            "study_population": study_pop.id,
        }

        if overrides is not None:
            data.update(overrides)

        return data

    def test_permissions(self, db_keys):
        url = reverse("epi:api:set-list")
        generic_perm_tester(url, self.get_upload_data())

    def test_bad_requests(self, db_keys):
        url = reverse("epi:api:set-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        scenarios = (
            {"desc": "empty payload doesn't crash", "expected_code": 400, "data": {}},
            {
                "desc": "exposure must be valid",
                "expected_code": 400,
                "expected_keys": {"exposure"},
                "data": self.get_upload_data({"exposure": 999}),
            },
            {
                "desc": "study population must be valid",
                "expected_code": 400,
                "expected_keys": {"study_population"},
                "data": self.get_upload_data({"study_population": 999}),
            },
            {
                "desc": "cant have both study pop and outcome",
                "expected_code": 400,
                "data": self.get_upload_data({"outcome": generic_get_any(models.Outcome).id}),
            },
        )

        generic_test_scenarios(client, url, scenarios)

    def test_valid_requests(self, db_keys):
        url = reverse("epi:api:set-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        just_created_comparison_set_id = None

        base_data = self.get_upload_data()

        def comparison_set_lookup_test(resp):
            nonlocal just_created_comparison_set_id

            comparison_set_id = resp.json()["id"]
            comparison_set = models.ComparisonSet.objects.get(id=comparison_set_id)
            assert comparison_set.name == base_data["name"]

            if just_created_comparison_set_id is None:
                just_created_comparison_set_id = comparison_set_id

        def altered_comparison_set_test(resp):
            nonlocal just_created_comparison_set_id

            comparison_set_id = resp.json()["id"]
            comparison_set = models.ComparisonSet.objects.get(id=comparison_set_id)
            assert comparison_set.name == "updated"
            assert comparison_set_id == just_created_comparison_set_id

        def deleted_comparison_set_test(resp):
            nonlocal just_created_comparison_set_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.ComparisonSet.objects.get(id=just_created_comparison_set_id)

        NoExp = self.get_upload_data()
        NoExp.pop("exposure")
        NoExpOrSP = self.get_upload_data({"outcome": generic_get_any(models.Outcome).id})
        NoExpOrSP.pop("exposure")
        NoExpOrSP.pop("study_population")
        create_scenarios = (
            {
                "desc": "basic comparison_set creation",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data(),
                "post_request_test": comparison_set_lookup_test,
            },
            {
                "desc": "no exposure comparison_set creation",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": NoExp,
                "post_request_test": comparison_set_lookup_test,
            },
            {
                "desc": "comparison_set creation with outcome, no exposure or study pop",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": NoExpOrSP,
                "post_request_test": comparison_set_lookup_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        url = f"{url}{just_created_comparison_set_id}/"
        update_scenarios = (
            {
                "desc": "basic comparison_set update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"name": "updated"},
                "method": "PATCH",
                "post_request_test": altered_comparison_set_test,
            },
        )
        generic_test_scenarios(client, url, update_scenarios)

        delete_scenarios = (
            {
                "desc": "comparison_set delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_comparison_set_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)


@pytest.mark.django_db
class TestGroupApi:
    def get_upload_data(self, overrides=None):
        comparison_set = generic_get_any(models.ComparisonSet)

        data = {
            "name": "test group",
            "comparison_set": comparison_set.id,
            "group_id": 0,
            "numeric": 1,
            "comparative_name": "comparative name",
            "sex": "F",
            "eligible_n": 500,
            "invited_n": 250,
            "participant_n": 10,
            "isControl": True,
            "comments": "test comments",
            "ethnicities": [],
        }

        if overrides is not None:
            data.update(overrides)

        return data

    def test_permissions(self, db_keys):
        url = reverse("epi:api:group-list")
        generic_perm_tester(url, self.get_upload_data())

    def test_bad_requests(self, db_keys):
        url = reverse("epi:api:group-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        scenarios = (
            {"desc": "empty payload doesn't crash", "expected_code": 400, "data": {}},
            {
                "desc": "comparison set must be valid",
                "expected_code": 400,
                "expected_keys": {"comparison_set"},
                "data": self.get_upload_data({"comparison_set": 999}),
            },
            {
                "desc": "sex must be a valid choice",
                "expected_code": 400,
                "expected_keys": {"sex"},
                "data": self.get_upload_data({"sex": "invalid choice"}),
            },
            {
                "desc": "ethnicities cannot be an invalid id",
                "expected_code": 400,
                "data": self.get_upload_data({"ethnicities": [999]}),
            },
            {
                "desc": "ethnicities cannot be an invalid string",
                "expected_code": 400,
                "data": self.get_upload_data({"ethnicities": ["not a real option"]}),
            },
            {
                "desc": "eligible/isControl/etc. need valid values",
                "expected_code": 400,
                "expected_keys": {"eligible_n", "isControl"},
                "data": self.get_upload_data({"eligible_n": "not numeric", "isControl": {}}),
            },
        )

        generic_test_scenarios(client, url, scenarios)

    def test_valid_requests(self, db_keys):
        url = reverse("epi:api:group-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        ethnicity = generic_get_any(models.Ethnicity)

        just_created_group_id = None

        base_data = self.get_upload_data()

        def group_lookup_test(resp):
            nonlocal just_created_group_id

            group_id = resp.json()["id"]
            group = models.Group.objects.get(id=group_id)
            assert group.name == base_data["name"]

            if just_created_group_id is None:
                just_created_group_id = group_id

        def group_lookup_tests_with_ethnicities(resp):
            group_id = resp.json()["id"]
            group = models.Group.objects.get(id=group_id)
            assert group.name == base_data["name"]

            found_ethnicity = False
            for e in group.ethnicities.all():
                if e.id == ethnicity.id:
                    found_ethnicity = True

            assert found_ethnicity is True

        def altered_group_test(resp):
            nonlocal just_created_group_id

            group_id = resp.json()["id"]
            group = models.Group.objects.get(id=group_id)
            assert group.name == "updated"
            assert group_id == just_created_group_id

        def deleted_group_test(resp):
            nonlocal just_created_group_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.Group.objects.get(id=just_created_group_id)

        create_scenarios = (
            {
                "desc": "basic group creation",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data(),
                "post_request_test": group_lookup_test,
            },
            {
                "desc": "create with named sex",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data({"sex": "female"}),
                "post_request_test": group_lookup_test,
            },
            {
                "desc": "include ethnicities by name",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data({"ethnicities": [ethnicity.name.lower()]}),
                "post_request_test": group_lookup_tests_with_ethnicities,
            },
            {
                "desc": "include ethnicities by id",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data({"ethnicities": [ethnicity.id]}),
                "post_request_test": group_lookup_tests_with_ethnicities,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        url = f"{url}{just_created_group_id}/"
        update_scenarios = (
            {
                "desc": "basic group update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"name": "updated"},
                "method": "PATCH",
                "post_request_test": altered_group_test,
            },
        )
        generic_test_scenarios(client, url, update_scenarios)

        delete_scenarios = (
            {
                "desc": "group delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_group_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)


@pytest.mark.django_db
class TestGroupNumericalDescriptionsApi:
    def get_upload_data(self, overrides=None):
        group = generic_get_any(models.Group)

        data = {
            "description": "test description",
            "group": group.id,
            "mean": 1.0,
            "mean_type": "mean",
            "variance_type": "SD",
            "lower_type": "other",
            "upper_type": "other",
        }

        if overrides is not None:
            data.update(overrides)

        return data

    def test_permissions(self, db_keys):
        url = reverse("epi:api:numerical-descriptions-list")
        generic_perm_tester(url, self.get_upload_data())

    def test_bad_requests(self, db_keys):
        url = reverse("epi:api:numerical-descriptions-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        scenarios = (
            {"desc": "empty payload doesn't crash", "expected_code": 400, "data": {}},
            {
                "desc": "group must be valid",
                "expected_code": 400,
                "expected_keys": {"group"},
                "data": self.get_upload_data({"group": 999}),
            },
            {
                "desc": "mean must be numeric",
                "expected_code": 400,
                "expected_keys": {"mean"},
                "data": self.get_upload_data({"mean": "not numeric"}),
            },
            {
                "desc": "if numeric, mean/variance/lower/upper types must be valid ids",
                "expected_code": 400,
                "expected_keys": {"mean_type", "variance_type", "lower_type", "upper_type"},
                "data": self.get_upload_data(
                    {"mean_type": 999, "variance_type": 999, "lower_type": 999, "upper_type": 999},
                ),
            },
            {
                "desc": "if strings, mean/variance/lower/upper types must be valid values",
                "expected_code": 400,
                "expected_keys": {"mean_type", "variance_type", "lower_type", "upper_type"},
                "data": self.get_upload_data(
                    {
                        "mean_type": "bad value 1",
                        "variance_type": "bad value 2",
                        "lower_type": "bad value 3",
                        "upper_type": "bad value 4",
                    }
                ),
            },
        )

        generic_test_scenarios(client, url, scenarios)

    def test_valid_requests(self, db_keys):
        url = reverse("epi:api:numerical-descriptions-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        just_created_numdesc_id = None

        base_data = self.get_upload_data()

        def numdesc_lookup_test(resp):
            nonlocal just_created_numdesc_id

            numdesc_id = resp.json()["id"]
            numdesc = models.GroupNumericalDescriptions.objects.get(id=numdesc_id)
            assert numdesc.description == base_data["description"]

            if just_created_numdesc_id is None:
                just_created_numdesc_id = numdesc_id

        def altered_numdesc_test(resp):
            nonlocal just_created_numdesc_id

            numdesc_id = resp.json()["id"]
            numdesc = models.GroupNumericalDescriptions.objects.get(id=numdesc_id)
            assert numdesc.description == "updated"
            assert numdesc_id == just_created_numdesc_id

        def deleted_numdesc_test(resp):
            nonlocal just_created_numdesc_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.GroupNumericalDescriptions.objects.get(id=just_created_numdesc_id)

        create_scenarios = (
            {
                "desc": "basic numdesc creation",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data(),
                "post_request_test": numdesc_lookup_test,
            },
            {
                "desc": "numdesc creation with id values for types",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data(
                    {
                        "mean_type": constants.GroupMeanType.MEAN,
                        "variance_type": constants.GroupVarianceType.SD,
                        "lower_type": constants.LowerLimit.LL,
                        "upper_type": constants.UpperLimit.UL,
                    }
                ),
                "post_request_test": numdesc_lookup_test,
            },
            {
                "desc": "numdesc creation with case-insensitive string values for types",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data(
                    {
                        "mean_type": (constants.GroupMeanType.MEAN.label).upper(),
                        "variance_type": (constants.GroupVarianceType.SD.label).upper(),
                        "lower_type": (constants.LowerLimit.LL.label).upper(),
                        "upper_type": (constants.UpperLimit.UL.label).upper(),
                    }
                ),
                "post_request_test": numdesc_lookup_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        url = f"{url}{just_created_numdesc_id}/"
        update_scenarios = (
            {
                "desc": "basic numdesc update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"description": "updated"},
                "method": "PATCH",
                "post_request_test": altered_numdesc_test,
            },
        )
        generic_test_scenarios(client, url, update_scenarios)

        delete_scenarios = (
            {
                "desc": "numdesc delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_numdesc_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)


@pytest.mark.django_db
class TestExposureApi:
    def get_upload_data(self, overrides=None):
        study_pop = generic_get_any(models.StudyPopulation)
        dose_unit = generic_get_any(DoseUnits)

        data = {
            "name": "test expo",
            "metric_description": "test description",
            "metric": "test metric",
            "analytical_method": "test method",
            "dtxsid": "DTXSID6026296",
            "inhalation": True,
            "measured": "measurement data",
            "sampling_period": "sample period data",
            "age_of_exposure": 1,
            "duration": "duration data",
            "exposure_distribution": "distro data",
            "study_population": study_pop.id,
            "metric_units": dose_unit.id,
            "n": 9,
            "description": "desc",
            "central_tendencies": [
                {
                    "estimate": 12,
                    "estimate_type": 2,
                    "variance": 5.5,
                    "variance_type": "SD",
                    "lower_ci": 4,
                    "upper_ci": 99,
                    "lower_range": 1.2,
                    "upper_range": 1.5,
                    "description": "description",
                }
            ],
        }

        if overrides is not None:
            data.update(overrides)

        return data

    def test_permissions(self, db_keys):
        url = reverse("epi:api:exposure-list")
        generic_perm_tester(url, self.get_upload_data())

    def test_bad_requests(self, db_keys):
        url = reverse("epi:api:exposure-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        scenarios = (
            {"desc": "empty payload doesn't crash", "expected_code": 400, "data": {}},
            {
                "desc": "dtxsid must be a existing/importable one",
                "expected_code": 400,
                "expected_content": "does not exist and could not be imported",
                "data": self.get_upload_data({"dtxsid": "bad value"}),
            },
            {
                "desc": "match data types",
                "expected_code": 400,
                "expected_keys": {"inhalation", "n"},  # etc.
                "data": self.get_upload_data({"inhalation": "truish", "n": "not numeric"}),
            },
            {
                "desc": "study pop must be valid",
                "expected_code": 400,
                "expected_keys": {"study_population"},
                "data": self.get_upload_data({"study_population": 999}),
            },
            {
                "desc": "at least one central tendency is required",
                "expected_code": 400,
                "expected_content": "At least one",
                "data": self.get_upload_data({"central_tendencies": None}),
            },
        )

        generic_test_scenarios(client, url, scenarios)

    @pytest.mark.vcr  # cache epa actor webservice response
    def test_valid_requests(self, db_keys):
        url = reverse("epi:api:exposure-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        dose_unit = generic_get_any(DoseUnits)

        just_created_exposure_id = None

        new_dtxsid = "DTXSID1020190"

        base_data = self.get_upload_data()

        def exposure_lookup_test(resp):
            nonlocal just_created_exposure_id

            exposure_id = resp.json()["id"]
            exposure = models.Exposure.objects.get(id=exposure_id)
            assert exposure.name == base_data["name"]

            if just_created_exposure_id is None:
                just_created_exposure_id = exposure_id

        def exposure_lookup_test_with_new_dtxsid(resp):
            exposure_id = resp.json()["id"]
            exposure = models.Exposure.objects.get(id=exposure_id)
            assert exposure.name == base_data["name"]
            assert exposure.dtxsid.dtxsid == new_dtxsid

        def exposure_lookup_test_with_new_metric_unit(resp):
            exposure_id = resp.json()["id"]
            exposure = models.Exposure.objects.get(id=exposure_id)
            assert exposure.name == base_data["name"]

            metric_units = exposure.metric_units
            assert metric_units.name == "on the fly"

        def altered_exposure_test(resp):
            nonlocal just_created_exposure_id

            exposure_id = resp.json()["id"]
            exposure = models.Exposure.objects.get(id=exposure_id)
            assert exposure.name == "updated"
            assert exposure_id == just_created_exposure_id

        def deleted_exposure_test(resp):
            nonlocal just_created_exposure_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.Exposure.objects.get(id=just_created_exposure_id)

        create_scenarios = (
            {
                "desc": "basic exposure creation",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data(),
                "post_request_test": exposure_lookup_test,
            },
            {
                "desc": "on the fly dtxsid creation",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data({"dtxsid": new_dtxsid}),
                "post_request_test": exposure_lookup_test_with_new_dtxsid,
            },
            {
                "desc": "dose unit by name",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data({"metric_units": dose_unit.name}),
                "post_request_test": exposure_lookup_test,
            },
            {
                "desc": "new dose unit",
                "expected_code": 400,
                "expected_keys": {"metric_units"},
                "data": self.get_upload_data({"metric_units": "on the fly"}),
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        url = f"{url}{just_created_exposure_id}/"
        update_scenarios = (
            {
                "desc": "basic exposure update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"name": "updated"},
                "method": "PATCH",
                "post_request_test": altered_exposure_test,
            },
        )
        generic_test_scenarios(client, url, update_scenarios)

        delete_scenarios = (
            {
                "desc": "exposure delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_exposure_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)


@pytest.mark.django_db
class TestMetadataApi:
    def test_permissions(self):
        # Disable non-assessment-specific list view of metadata
        with pytest.raises(NoReverseMatch):
            url = reverse("epi:api:metadata-list")

        client = APIClient()

        # Public should NOT be able to view the version for private assessments
        private_assessment = Assessment.objects.filter(public_on__isnull=True).first()
        assert private_assessment is not None
        url = reverse("epi:api:metadata-detail", args=(private_assessment.id,))
        resp = client.get(url)
        assert resp.status_code == 403

    def verify_keys_in_response(self, data, keys):
        for key in keys:
            sub_keys = keys[key]
            assert key in data
            sub_data = data[key]

            for sub_key in sub_keys:
                assert sub_key in sub_data

    def verify_keys_not_in_response(self, data, keys):
        for key in keys:
            sub_keys = keys[key]

            if key in data:
                sub_data = data[key]

                for sub_key in sub_keys:
                    assert sub_key not in sub_data

    def test_bad_request(self, rewrite_data_files: bool, db_keys):
        # Invalid assessment id
        client = APIClient()
        url = reverse("epi:api:metadata-detail", args=("999",))
        resp = client.get(url)
        assert resp.status_code == 404

    def test_metadata(self, rewrite_data_files: bool, db_keys):
        # Verify that we get at least the correct structure of data back
        expected_keys = {
            "study_population": {"design", "countries", "assessment_specific_criteria"},
            "outcome": {"diagnostic"},
            "result": {
                "dose_response",
                "statistical_power",
                "estimate_type",
                "variance_type",
                "metrics",
                "assessment_specific_adjustment_factors",
            },
            "group_result": {"p_value_qualifier", "main_finding"},
            "group": {"sex", "ethnicities"},
            "group_numerical_descriptions": {
                "mean_type",
                "variance_type",
                "lower_type",
                "upper_type",
            },
            "exposure": {"dose_units"},
            "central_tendency": {"estimate_type", "variance_type"},
        }

        client = APIClient()

        assert client.login(username="admin@hawcproject.org", password="pw") is True
        url = reverse("epi:api:metadata-detail", args=("2",))
        resp = client.get(url)
        assert resp.status_code == 200
        self.verify_keys_in_response(resp.data, expected_keys)


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
            assert (scenario["expected_keys"]).issubset(response.data.keys())

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
