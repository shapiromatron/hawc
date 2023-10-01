from copy import deepcopy

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.urls import reverse
from rest_framework.test import APIClient

from hawc.apps.assessment.models import Log
from hawc.apps.epiv2 import models

from ..test_utils import check_200, check_403, check_api_json_data, get_client


@pytest.mark.django_db
class TestEpiAssessmentViewSet:
    def test_export(self, rewrite_data_files):
        url = reverse("epiv2:api:assessment-export", args=(1,))
        client = get_client(api=True)

        # anon get 403
        check_403(client, url)

        # pm can get valid response
        client = get_client("pm", api=True)
        response = check_200(client, url + "?unpublished=true")
        key = "api-epiv2-export-1.json"
        check_api_json_data(response.json(), key, rewrite_data_files)

    def test_study_export(self, rewrite_data_files):
        url = reverse("epiv2:api:assessment-study-export", args=(1,))

        # anon get 403
        check_403(get_client(api=True), url)

        # pm can get valid response
        response = check_200(get_client("pm", api=True), url + "?unpublished=true")
        assert len(response.json()) == 1
        key = "api-epiv2-study-export-1.json"
        check_api_json_data(response.json(), key, rewrite_data_files)


@pytest.mark.django_db
class TestDesignViewSet:
    def test_permissions(self, db_keys):
        url = reverse("epiv2:api:design-list")
        data = {
            "study_id": db_keys.study_working,
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
            "age_profile": ["AD"],
            "countries": ["TW"],
        }
        generic_perm_tester(url, data)

    def test_valid_requests(self, db_keys):
        url = reverse("epiv2:api:design-list")
        client = APIClient()
        assert client.login(username="team@hawcproject.org", password="pw") is True

        data = {
            "study_id": db_keys.study_working,
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
            "age_profile": ["AD"],
            "countries": ["TW"],
        }
        data2 = deepcopy(data)
        data2.pop("age_profile")

        just_created_design_id = None

        def design_create_test(resp):
            nonlocal just_created_design_id

            design_id = resp.json()["id"]
            design = models.Design.objects.get(id=design_id)
            country = models.Country.objects.get(code="TW")
            assert design.source == "GP"
            assert design.summary == data["summary"]
            assert design.countries.get(code="TW") == country

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
                "post_request_test": design_create_test,
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
            {
                "desc": "countries and age profiles update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"countries": ["JP", "DK"], "age_profile": ["AD", "other"]},
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
                "expected_keys": {"study_id"},
                "data": {},
            },
            {
                "desc": "valid study id req'd",
                "expected_code": 400,
                "expected_keys": {"study_id"},
                "data": {"study": -1},
            },
            {
                "desc": "invalid country",
                "expected_code": 400,
                "expected_keys": {"countries"},
                "expected_content": "is not a country",
                "data": {"countries": ["XX"]},
            },
            {
                "desc": "invalid study_design",
                "expected_code": 400,
                "expected_keys": {"study_design"},
                "expected_content": "not a valid choice",
                "data": {"study_design": "XX"},
            },
            {
                "desc": "invalid age_profile",
                "expected_code": 400,
                "expected_keys": {"age_profile"},
                "expected_content": "contained invalid value(s)",
                "data": {"age_profile": ["XX", "xx"]},
            },
            {
                "desc": "invalid source",
                "expected_code": 400,
                "expected_keys": {"source"},
                "expected_content": "not a valid choice",
                "data": {"source": "XX"},
            },
            {
                "desc": "invalid sex",
                "expected_code": 400,
                "expected_keys": {"sex"},
                "expected_content": "not a valid choice",
                "data": {"sex": "XX"},
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
        generic_test_scenario(client, url, scenario)


def generic_test_scenario(client, url, scenario):
    method = scenario.get("method", "POST")
    if method.upper() == "POST":
        response = client.post(url, scenario["data"], format="json")
    elif method.upper() == "PATCH":
        response = client.patch(url, scenario["data"], format="json")
    elif method.upper() == "DELETE":
        response = client.delete(url)
    else:
        raise ValueError("Unknown method")

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


@pytest.mark.django_db
class TestMetadataViewSet:
    def test_permissions(self):
        url = reverse("epiv2:api:metadata-list")
        # public should have access to this metadata
        client = APIClient()
        resp = client.get(url)
        assert resp.status_code == 200

    def test_metadata(self, rewrite_data_files: bool):
        fn = "api-epiv2-metadata.json"
        url = reverse("epiv2:api:metadata-list") + "?format=json"
        client = APIClient()
        resp = client.get(url)
        assert resp.status_code == 200

        data = resp.json()
        check_api_json_data(data, fn, rewrite_data_files)


@pytest.mark.django_db
class TestChemicalViewSet:
    def get_upload_data(self, overrides=None):
        design = generic_get_any(models.Design)

        data = {
            "design": design.id,
            "name": "sample chemical via api",
            "dsstox_id": "DTXSID6026296",
        }

        if overrides is not None:
            data.update(overrides)

        return data

    def test_permissions(self, db_keys):
        url = reverse("epiv2:api:chemical-list")
        generic_perm_tester(url, self.get_upload_data())

    def test_bad_requests(self, db_keys):
        url = reverse("epiv2:api:chemical-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        scenarios = (
            {"desc": "empty payload doesn't crash", "expected_code": 400, "data": {}},
            {
                "desc": "non-legal value for dsstox",
                "expected_code": 400,
                "expected_content": "object does not exist",
                "data": self.get_upload_data({"dsstox_id": "invalid_id"}),
            },
            {
                "desc": "missing design",
                "expected_code": 400,
                "expected_content": "may not be null",
                "data": self.get_upload_data({"design": None}),
            },
        )

        generic_test_scenarios(client, url, scenarios)

    def test_valid_requests(self, db_keys):
        url = reverse("epiv2:api:chemical-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        just_created_chemical_id = None
        base_data = self.get_upload_data()

        def chemical_lookup_test(resp):
            nonlocal just_created_chemical_id

            chem_id = resp.json()["id"]
            chemical = models.Chemical.objects.get(id=chem_id)
            assert chemical.name == base_data["name"]

            if just_created_chemical_id is None:
                just_created_chemical_id = chem_id

        def altered_chemical_name_test(resp):
            nonlocal just_created_chemical_id

            chem_id = resp.json()["id"]
            chemical = models.Chemical.objects.get(id=chem_id)
            assert chemical.name == "updated"
            assert chem_id == just_created_chemical_id

        def altered_chemical_dtxsid_test(resp):
            chem_id = resp.json()["id"]
            chemical = models.Chemical.objects.get(id=chem_id)
            assert chemical.dsstox.dtxsid == "DTXSID7020970"

        def deleted_chemical_test(resp):
            nonlocal just_created_chemical_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.Chemical.objects.get(id=just_created_chemical_id)

        create_scenarios = (
            {
                "desc": "basic chemical creation",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data(),
                "post_request_test": chemical_lookup_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        url = f"{url}{just_created_chemical_id}/"
        update_scenarios = (
            {
                "desc": "name update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"name": "updated"},
                "method": "PATCH",
                "post_request_test": altered_chemical_name_test,
            },
            {
                "desc": "dtxsid update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"dsstox_id": "DTXSID7020970"},
                "method": "PATCH",
                "post_request_test": altered_chemical_dtxsid_test,
            },
        )
        generic_test_scenarios(client, url, update_scenarios)

        delete_scenarios = (
            {
                "desc": "chemical delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_chemical_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)


@pytest.mark.django_db
class TestExposureViewSet:
    def get_upload_data(self, overrides=None):
        design = generic_get_any(models.Design)

        data = {
            "design": design.id,
            "exposure_route": "IH",
            "name": "sample expo via api",
            "measurement_type": ["Questionnaire", "Modeled"],
            "biomonitoring_matrix": "UR",
            "biomonitoring_source": "ML",
            "measurement_timing": "cross-sectional",
            "measurement_method": "test case method details here",
            "comments": "test case comments here",
        }

        if overrides is not None:
            data.update(overrides)

        return data

    def test_permissions(self, db_keys):
        url = reverse("epiv2:api:exposure-list")
        generic_perm_tester(url, self.get_upload_data())

    def test_bad_requests(self, db_keys):
        url = reverse("epiv2:api:exposure-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        scenarios = (
            {"desc": "empty payload doesn't crash", "expected_code": 400, "data": {}},
            {
                "desc": "non-legal value for biomonitoring matrix",
                "expected_code": 400,
                "expected_keys": {"biomonitoring_matrix"},
                "data": self.get_upload_data({"biomonitoring_matrix": "XX"}),
            },
            {
                "desc": "non-legal value for exposure route",
                "expected_code": 400,
                "expected_keys": {"exposure_route"},
                "data": self.get_upload_data({"exposure_route": "XX"}),
            },
            {
                "desc": "design must be valid",
                "expected_code": 400,
                "expected_keys": {"design"},
                "expected_content": "object does not exist",
                "data": self.get_upload_data({"design": 999}),
            },
            {
                "desc": "missing design",
                "expected_code": 400,
                "expected_content": "may not be null",
                "data": self.get_upload_data({"design": None}),
            },
        )

        generic_test_scenarios(client, url, scenarios)

    def test_valid_requests(self, db_keys):
        url = reverse("epiv2:api:exposure-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        just_created_exposure_id = None
        base_data = self.get_upload_data()

        def exposure_lookup_test(resp):
            nonlocal just_created_exposure_id

            exposure_id = resp.json()["id"]
            exposure = models.Exposure.objects.get(id=exposure_id)
            assert exposure.name == base_data["name"]

            if just_created_exposure_id is None:
                just_created_exposure_id = exposure_id

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
            {
                "desc": "case-insensitive readable values instead of enum codes",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {
                    "exposure_route": "DeRmAl",
                    "biomonitoring_matrix": "SALIVA",
                    "biomonitoring_source": "matERNAL",
                },
                "method": "PATCH",
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
class TestExposureLevelViewSet:
    def get_upload_data(self, overrides=None):
        design = generic_get_any(models.Design)
        chemical = models.Chemical.objects.filter(design=design.id).first()
        exposure = models.Exposure.objects.filter(design=design.id).first()

        data = {
            "name": "test exposure level creation",
            "sub_population": "test subpop",
            "median": 1,
            "mean": 2,
            "variance": 3,
            "variance_type": 1,
            "units": "ng",
            "ci_lcl": "4",
            "percentile_25": "5",
            "percentile_75": "6",
            "ci_ucl": "7",
            "ci_type": "Rng",
            "negligible_exposure": "8",
            "data_location": "99",
            "comments": "expolev comments a",
            "design": design.id,
            "chemical_id": chemical.id,
            "exposure_measurement_id": exposure.id,
        }

        if overrides is not None:
            data.update(overrides)

        return data

    def test_permissions(self, db_keys):
        url = reverse("epiv2:api:exposure-level-list")
        generic_perm_tester(url, self.get_upload_data())

    def test_bad_requests(self, db_keys):
        url = reverse("epiv2:api:exposure-level-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        base_data = self.get_upload_data()
        base_data_design_id = base_data["design"]
        non_design_chemical = models.Chemical.objects.filter(~Q(design=base_data_design_id)).first()
        non_design_exposure = models.Exposure.objects.filter(~Q(design=base_data_design_id)).first()

        scenarios = (
            {"desc": "empty payload doesn't crash", "expected_code": 400, "data": {}},
            {
                "desc": "non-existent value for chemical",
                "expected_code": 400,
                "expected_content": "object does not exist",
                "data": self.get_upload_data({"chemical_id": -1}),
            },
            {
                "desc": "non-existent value for exposure",
                "expected_code": 400,
                "expected_content": "object does not exist",
                "data": self.get_upload_data({"exposure_measurement_id": -1}),
            },
            {
                "desc": "chemical that exists but is not part of this design",
                "expected_code": 400,
                "expected_content": "does not belong to the correct design",
                "data": self.get_upload_data({"chemical_id": non_design_chemical.id}),
            },
            {
                "desc": "exposure that exists but is not part of this design",
                "expected_code": 400,
                "expected_content": "does not belong to the correct design",
                "data": self.get_upload_data({"exposure_measurement_id": non_design_exposure.id}),
            },
            {
                "desc": "illegal variance_type",
                "expected_code": 400,
                "expected_content": "not a valid choice",
                "data": self.get_upload_data({"variance_type": -1}),
            },
            {
                "desc": "illegal lower/upper interval type",
                "expected_code": 400,
                "expected_content": "not a valid choice",
                "data": self.get_upload_data({"ci_type": "xyz"}),
            },
            {
                "desc": "missing design",
                "expected_code": 400,
                "expected_content": "may not be null",
                "data": self.get_upload_data({"design": None}),
            },
        )

        generic_test_scenarios(client, url, scenarios)

    def test_valid_requests(self, db_keys):
        url = reverse("epiv2:api:exposure-level-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        just_created_expolev_id = None
        base_data = self.get_upload_data()

        base_data_design_id = base_data["design"]
        other_design = models.Design.objects.filter(~Q(id=base_data_design_id)).first()
        other_chem = models.Chemical.objects.filter(design=other_design.id).first()
        other_exposure = models.Exposure.objects.filter(design=other_design.id).first()

        def expolevel_lookup_test(resp):
            nonlocal just_created_expolev_id

            expolev_id = resp.json()["id"]
            expolevel = models.ExposureLevel.objects.get(id=expolev_id)
            assert expolevel.name == base_data["name"]

            if just_created_expolev_id is None:
                just_created_expolev_id = expolev_id

        def altered_expolevel_name_test(resp):
            nonlocal just_created_expolev_id

            expolev_id = resp.json()["id"]
            expolevel = models.ExposureLevel.objects.get(id=expolev_id)
            assert expolevel.name == "updated expolev"
            assert expolev_id == just_created_expolev_id

        def deleted_expolevel_test(resp):
            nonlocal just_created_expolev_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.ExposureLevel.objects.get(id=just_created_expolev_id)

        create_scenarios = (
            {
                "desc": "basic expolevel creation",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data(),
                "post_request_test": expolevel_lookup_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        url = f"{url}{just_created_expolev_id}/"
        update_scenarios = (
            {
                "desc": "name update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"name": "updated expolev"},
                "method": "PATCH",
                "post_request_test": altered_expolevel_name_test,
            },
            {
                "desc": "design/chemical/exposuremeasurement legal update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {
                    "design": other_design.id,
                    "chemical_id": other_chem.id,
                    "exposure_measurement_id": other_exposure.id,
                },
                "method": "PATCH",
            },
            {
                "desc": "legal variance/ci type modifications",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"ci_type": "P90", "variance_type": 5},
                "method": "PATCH",
            },
            {
                "desc": "case-insensitive readable values instead of enum codes",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"variance_type": "GsD", "ci_type": "10th/90th percentile"},
                "method": "PATCH",
            },
        )
        generic_test_scenarios(client, url, update_scenarios)

        delete_scenarios = (
            {
                "desc": "expolevel delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_expolevel_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)


@pytest.mark.django_db
class TestOutcomeViewSet:
    def get_upload_data(self, overrides=None):
        design = generic_get_any(models.Design)

        data = {
            "system": "OC",
            "effect": "eye stuff",
            "effect_detail": "eye detail here",
            "endpoint": "eye endpoint here",
            "comments": "comments here",
            "design": design.id,
        }

        if overrides is not None:
            data.update(overrides)

        return data

    def test_permissions(self, db_keys):
        url = reverse("epiv2:api:outcome-list")
        generic_perm_tester(url, self.get_upload_data())

    def test_bad_requests(self, db_keys):
        url = reverse("epiv2:api:outcome-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        scenarios = (
            {"desc": "empty payload doesn't crash", "expected_code": 400, "data": {}},
            {
                "desc": "invalid system",
                "expected_code": 400,
                "expected_content": "not a valid choice",
                "data": self.get_upload_data({"system": "bad system"}),
            },
            {
                "desc": "missing design",
                "expected_code": 400,
                "expected_content": "may not be null",
                "data": self.get_upload_data({"design": None}),
            },
        )

        generic_test_scenarios(client, url, scenarios)

    def test_valid_requests(self, db_keys):
        url = reverse("epiv2:api:outcome-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        just_created_outcome_id = None
        base_data = self.get_upload_data()

        def outcome_lookup_test(resp):
            nonlocal just_created_outcome_id

            outcome_id = resp.json()["id"]
            outcome = models.Outcome.objects.get(id=outcome_id)
            assert outcome.effect_detail == base_data["effect_detail"]

            if just_created_outcome_id is None:
                just_created_outcome_id = outcome_id

        def altered_outcome_test(resp):
            nonlocal just_created_outcome_id

            outcome_id = resp.json()["id"]
            outcome = models.Outcome.objects.get(id=outcome_id)
            assert outcome.effect_detail == "altered detail"
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
                "data": self.get_upload_data(),
                "post_request_test": outcome_lookup_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        url = f"{url}{just_created_outcome_id}/"
        update_scenarios = (
            {
                "desc": "name update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"effect_detail": "altered detail"},
                "method": "PATCH",
                "post_request_test": altered_outcome_test,
            },
            {
                "desc": "valid system update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {
                    "system": "CA",
                },
                "method": "PATCH",
            },
            {
                "desc": "case-insensitive readable values instead of enum codes",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"system": "mEtAbOlIc"},
                "method": "PATCH",
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
class TestAdjustmentFactorViewSet:
    def get_upload_data(self, overrides=None):
        design = generic_get_any(models.Design)

        data = {
            "name": "test name for adjfac",
            "description": "test description for adjfac",
            "comments": "test comments made via api",
            "design": design.id,
        }

        if overrides is not None:
            data.update(overrides)

        return data

    def test_permissions(self, db_keys):
        url = reverse("epiv2:api:adjustment-factor-list")
        generic_perm_tester(url, self.get_upload_data())

    def test_bad_requests(self, db_keys):
        url = reverse("epiv2:api:adjustment-factor-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        scenarios = (
            {"desc": "empty payload doesn't crash", "expected_code": 400, "data": {}},
            {
                "desc": "missing design",
                "expected_code": 400,
                "expected_content": "may not be null",
                "data": self.get_upload_data({"design": None}),
            },
        )

        generic_test_scenarios(client, url, scenarios)

    def test_valid_requests(self, db_keys):
        url = reverse("epiv2:api:adjustment-factor-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        just_created_adjustment_factor_id = None
        base_data = self.get_upload_data()

        def adjustment_factor_lookup_test(resp):
            nonlocal just_created_adjustment_factor_id

            adjustment_factor_id = resp.json()["id"]
            adjustment_factor = models.AdjustmentFactor.objects.get(id=adjustment_factor_id)
            assert adjustment_factor.name == base_data["name"]

            if just_created_adjustment_factor_id is None:
                just_created_adjustment_factor_id = adjustment_factor_id

        def altered_adjustment_factor_test(resp):
            nonlocal just_created_adjustment_factor_id

            adjustment_factor_id = resp.json()["id"]
            adjustment_factor = models.AdjustmentFactor.objects.get(id=adjustment_factor_id)
            assert adjustment_factor.name == "altered adjfac name"
            assert adjustment_factor_id == just_created_adjustment_factor_id

        def deleted_adjustment_factor_test(resp):
            nonlocal just_created_adjustment_factor_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.AdjustmentFactor.objects.get(id=just_created_adjustment_factor_id)

        create_scenarios = (
            {
                "desc": "basic adjustmentfactor creation",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data(),
                "post_request_test": adjustment_factor_lookup_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        url = f"{url}{just_created_adjustment_factor_id}/"
        update_scenarios = (
            {
                "desc": "name update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"name": "altered adjfac name"},
                "method": "PATCH",
                "post_request_test": altered_adjustment_factor_test,
            },
        )
        generic_test_scenarios(client, url, update_scenarios)

        delete_scenarios = (
            {
                "desc": "adjustmentfactor delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_adjustment_factor_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)


@pytest.mark.django_db
class TestDataExtractionViewSet:
    def get_upload_data(self, overrides=None):
        design = generic_get_any(models.Design)
        outcome = models.Outcome.objects.filter(design=design.id).first()
        exposure_level = models.ExposureLevel.objects.filter(design=design.id).first()
        adjustment_factor = models.AdjustmentFactor.objects.filter(design=design.id).first()

        data = {
            "outcome_id": outcome.id,
            "exposure_level_id": exposure_level.id,
            "factors_id": adjustment_factor.id,
            "sub_population": "sub test",
            "outcome_measurement_timing": "outcome timing test",
            "effect_estimate_type": "Percent change",
            "effect_estimate": 1.1,
            "ci_lcl": 1.2,
            "ci_ucl": 1.3,
            "ci_type": "Rng",
            "units": "units test",
            "variance_type": 3,
            "variance": 1.4,
            "n": 999,
            "p_value": "1.5",
            "significant": 2,
            "group": "rg test",
            "exposure_rank": 1,
            "exposure_transform": "log(x+1)",
            "outcome_transform": "log10",
            "confidence": "confidence test",
            "data_location": "loc test",
            "effect_description": "description test",
            "statistical_method": "stat method test",
            "adverse_direction": "up",
            "comments": "comments test",
            "design": design.id,
        }

        if overrides is not None:
            data.update(overrides)

        return data

    def test_permissions(self, db_keys):
        url = reverse("epiv2:api:data-extraction-list")
        generic_perm_tester(url, self.get_upload_data())

    def test_bad_requests(self, db_keys):
        url = reverse("epiv2:api:data-extraction-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        base_data = self.get_upload_data()
        base_data_design_id = base_data["design"]
        non_design_outcome = models.Outcome.objects.filter(~Q(design=base_data_design_id)).first()
        non_design_exposure_level = models.ExposureLevel.objects.filter(
            ~Q(design=base_data_design_id)
        ).first()
        non_design_adjustment_factor = models.AdjustmentFactor.objects.filter(
            ~Q(design=base_data_design_id)
        ).first()

        scenarios = (
            {"desc": "empty payload doesn't crash", "expected_code": 400, "data": {}},
            {
                "desc": "missing design",
                "expected_code": 400,
                "expected_content": "may not be null",
                "data": self.get_upload_data({"design": None}),
            },
            {
                "desc": "missing outcome",
                "expected_code": 400,
                "expected_content": "may not be null",
                "data": self.get_upload_data({"outcome_id": None}),
            },
            {
                "desc": "missing exposure_level",
                "expected_code": 400,
                "expected_content": "may not be null",
                "data": self.get_upload_data({"exposure_level_id": None}),
            },
            {
                "desc": "outcome not part of design",
                "expected_code": 400,
                "expected_content": "does not belong to the correct design",
                "data": self.get_upload_data({"outcome_id": non_design_outcome.id}),
            },
            {
                "desc": "exposure_level not part of design",
                "expected_code": 400,
                "expected_content": "does not belong to the correct design",
                "data": self.get_upload_data({"exposure_level_id": non_design_exposure_level.id}),
            },
            {
                "desc": "adjustment factor not part of design",
                "expected_code": 400,
                "expected_content": "does not belong to the correct design",
                "data": self.get_upload_data({"outcome_id": non_design_adjustment_factor.id}),
            },
            {
                "desc": "invalid ci_type",
                "expected_code": 400,
                "expected_content": "not a valid choice",
                "data": self.get_upload_data({"ci_type": "bad ci type"}),
            },
            {
                "desc": "invalid variance type",
                "expected_code": 400,
                "expected_content": "not a valid choice",
                "data": self.get_upload_data({"variance_type": "bad variance_type"}),
            },
            {
                "desc": "invalid significant",
                "expected_code": 400,
                "expected_content": "not a valid choice",
                "data": self.get_upload_data({"significant": "bad significant"}),
            },
            {
                "desc": "invalid adverse_direction",
                "expected_code": 400,
                "expected_content": "not a valid choice",
                "data": self.get_upload_data({"adverse_direction": "dunno"}),
            },
        )

        generic_test_scenarios(client, url, scenarios)

    def test_valid_requests(self, db_keys):
        url = reverse("epiv2:api:data-extraction-list")
        client = APIClient()
        assert client.login(username="admin@hawcproject.org", password="pw") is True

        just_created_data_extraction_id = None
        base_data = self.get_upload_data()
        base_data_design_id = base_data["design"]
        other_design = models.Design.objects.filter(~Q(id=base_data_design_id)).first()
        other_outcome = models.Outcome.objects.filter(design=other_design.id).first()
        other_exposure_level = models.ExposureLevel.objects.filter(design=other_design.id).first()
        other_adjustment_factor = models.AdjustmentFactor.objects.filter(
            design=other_design.id
        ).first()

        def data_extraction_lookup_test(resp):
            nonlocal just_created_data_extraction_id

            data_extraction_id = resp.json()["id"]
            data_extraction = models.DataExtraction.objects.get(id=data_extraction_id)
            assert data_extraction.comments == base_data["comments"]

            if just_created_data_extraction_id is None:
                just_created_data_extraction_id = data_extraction_id

        def altered_data_extraction_test(resp):
            nonlocal just_created_data_extraction_id

            data_extraction_id = resp.json()["id"]
            data_extraction = models.DataExtraction.objects.get(id=data_extraction_id)
            assert data_extraction.comments == "altered data_extraction comments"
            assert data_extraction_id == just_created_data_extraction_id

        def deleted_data_extraction_test(resp):
            nonlocal just_created_data_extraction_id

            assert resp.data is None

            with pytest.raises(ObjectDoesNotExist):
                models.DataExtraction.objects.get(id=just_created_data_extraction_id)

        create_scenarios = (
            {
                "desc": "basic dataextraction creation",
                "expected_code": 201,
                "expected_keys": {"id"},
                "data": self.get_upload_data(),
                "post_request_test": data_extraction_lookup_test,
            },
        )
        generic_test_scenarios(client, url, create_scenarios)

        url = f"{url}{just_created_data_extraction_id}/"
        update_scenarios = (
            {
                "desc": "comments update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"comments": "altered data_extraction comments"},
                "method": "PATCH",
                "post_request_test": altered_data_extraction_test,
            },
            {
                "desc": "update ci_type/variance_type/significant by enum vals",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {"ci_type": "P90", "variance_type": 5, "significant": 1},
                "method": "PATCH",
            },
            {
                "desc": "case-insensitive readable values instead of enum codes",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {
                    "ci_type": "10TH/90TH PeRcEnTiLe",
                    "variance_type": "IQR (INTERQUARTILE range)",
                    "significant": "yEs",
                },
                "method": "PATCH",
            },
            {
                "desc": "design/outcome/exposure_level/adjustment_factor legal update",
                "expected_code": 200,
                "expected_keys": {"id"},
                "data": {
                    "design": other_design.id,
                    "outcome_id": other_outcome.id,
                    "exposure_level_id": other_exposure_level.id,
                    "adjustment_factor_id": other_adjustment_factor.id,
                },
                "method": "PATCH",
            },
        )
        generic_test_scenarios(client, url, update_scenarios)

        delete_scenarios = (
            {
                "desc": "dataextraction delete",
                "expected_code": 204,
                "method": "DELETE",
                "post_request_test": deleted_data_extraction_test,
            },
        )
        generic_test_scenarios(client, url, delete_scenarios)
