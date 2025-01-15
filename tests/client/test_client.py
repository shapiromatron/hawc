import json

import pandas as pd
import pytest
from django.core.cache import cache
from django.test import LiveServerTestCase, TestCase

import hawc.apps.epiv2.constants as epiv2constants
import hawc.apps.epiv2.models as epiv2models
from hawc.apps.animal.models import Experiment
from hawc.apps.assessment import constants
from hawc.apps.assessment.models import DoseUnits, Strain
from hawc.apps.epi.models import ResultMetric
from hawc.apps.lit.models import Reference, ReferenceFilterTag
from hawc.apps.myuser.models import HAWCUser
from hawc.apps.study import constants as studyconstants
from hawc.apps.study.models import Study
from hawc.apps.summary.models import DataPivot
from hawc_client import BaseClient, HawcClient, HawcClientException


@pytest.mark.usefixtures("set_db_keys")
class TestClient(LiveServerTestCase, TestCase):
    """
    We use a single class that inherits from both LiveServerTestCase and TestCase
    in order to supersede properties of LiveServerTestCase that cause the database to be flushed
    after every test, while still being able to utilize a live server for HTTP requests.

    Further reading: https://code.djangoproject.com/ticket/23640#comment:3

    """

    @pytest.fixture(scope="function", autouse=True)
    def clear_cache(cls):
        # Reset user authentication throttling
        cache.clear()

    #####################
    # HawcSession tests #
    #####################
    def test_set_authentication_token(self):
        client = HawcClient(self.live_server_url)
        with pytest.raises(HawcClientException) as err:
            client.set_authentication_token("123")
        assert err.value.status_code == 403

        url_private_api = f"{self.live_server_url}/assessment/api/assessment/1/"
        url_private_view = f"{self.live_server_url}/assessment/1/"

        for url in [url_private_api, url_private_view]:
            with pytest.raises(HawcClientException) as err:
                client.session.get(url)
            assert err.value.status_code == 403

        user = HAWCUser.objects.get(email="pm@hawcproject.org")
        token = user.get_api_token().key

        # login; create a DRF token-based session
        assert client.set_authentication_token(token, login=False) is True
        resp = client.session.get(url_private_api)
        assert resp.status_code == 200
        with pytest.raises(HawcClientException) as err:
            client.session.get(url_private_view)
        assert err.value.status_code == 403

        # login; create a Django based cookie session (CSRF tokens required)
        assert client.set_authentication_token(token, login=True) is True
        for url in [url_private_api, url_private_view]:
            resp = client.session.get(url)
            assert resp.status_code == 200

    ####################
    # BaseClient tests #
    ####################

    def test_csv_to_df(self):
        client = BaseClient(None)
        csv = "column1,column2,column3\na,b,c\n1,2,3"
        df = pd.DataFrame(
            data={"column1": ["a", "1"], "column2": ["b", "2"], "column3": ["c", "3"]}
        )
        assert client._csv_to_df(csv).equals(df)

    ######################
    # AnimalClient tests #
    ######################

    def test_animal_data(self):
        client = HawcClient(self.live_server_url)
        response = client.animal.data(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    def test_animal_metadata(self):
        client = HawcClient(self.live_server_url)
        response = client.animal.metadata()
        assert isinstance(response, dict)

    def test_animal_data_summary(self):
        client = HawcClient(self.live_server_url)
        response = client.animal.data_summary(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    def test_animal_bmds(self):
        client = HawcClient(self.live_server_url)
        response = client.animal.bmds_endpoints(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    def test_animal_endpoints(self):
        client = HawcClient(self.live_server_url)

        # list of endpoints
        response = client.animal.endpoints(2)
        assert isinstance(response, list)
        assert len(response) == 5
        assert response[0]["name"] == "Water T maze (learning error)"
        assert (
            response[0]["animal_group"]["experiment"]["study"]["short_citation"]
            == "Biesemeier JA et al. 2011"
        )

        # list of studies
        response = client.animal.endpoints(2, invert=True)
        assert isinstance(response, list)
        assert len(response) == 1
        assert (
            response[0]["experiments"][0]["animal_groups"][0]["endpoints"][0]["name"]
            == "Water T maze (learning error)"
        )
        assert response[0]["short_citation"] == "Biesemeier JA et al. 2011"

    def test_animal_create(self):
        """
        Test all the create methods.  This only checks the happy-path and confirms that the client
        methods work as intended.
        """
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")

        # experiment
        experiment_name = "30 day oral"
        data = dict(
            study_id=self.db_keys.study_working,
            name=experiment_name,
            type="St",
            has_multiple_generations=False,
            chemical="2,3,7,8-Tetrachlorodibenzo-P-dioxin",
            cas="1746-01-6",
            dtxsid="DTXSID6026296",
            chemical_source="ABC Inc.",
            purity_available=True,
            purity_qualifier="≥",
            purity=99.9,
            vehicle="DMSO",
            guideline_compliance="not reported",
            description="Details here.",
        )
        experiment = client.animal.create_experiment(data)
        assert isinstance(experiment, dict) and experiment["name"] == experiment_name

        # animal group + dosing regime + doses
        animal_group_name = "Female C57BL/6 Mice"
        strain = Strain.objects.first()
        data = dict(
            experiment_id=experiment["id"],
            name=animal_group_name,
            species=strain.species_id,
            strain=strain.id,
            sex="F",
            animal_source="Charles River",
            lifestage_exposed="Adult",
            lifestage_assessed="Adult",
            generation="",
            comments="Detailed comments here",
            diet="...",
            dosing_regime=dict(
                route_of_exposure="OR",
                duration_exposure=30,
                duration_exposure_text="30 days",
                duration_observation=180,
                num_dose_groups=3,
                positive_control=True,
                negative_control="VT",
                description="...",
                doses=[
                    {"dose_group_id": 0, "dose": 0, "dose_units_id": 1},
                    {"dose_group_id": 1, "dose": 50, "dose_units_id": 1},
                    {"dose_group_id": 2, "dose": 100, "dose_units_id": 1},
                    {"dose_group_id": 0, "dose": 0, "dose_units_id": 2},
                    {"dose_group_id": 1, "dose": 3.7, "dose_units_id": 2},
                    {"dose_group_id": 2, "dose": 11.4, "dose_units_id": 2},
                ],
            ),
        )
        animal_group = client.animal.create_animal_group(data)
        assert isinstance(experiment, dict) and animal_group["name"] == animal_group_name

        # endpoint + endpoint group
        data = dict(
            animal_group_id=animal_group["id"],
            name="Relative liver weight",
            name_term=5,
            system="Hepatic",
            system_term=1,
            organ="Liver",
            organ_term=2,
            effect="Organ weight",
            effect_term=3,
            effect_subtype="Relative weight",
            effect_subtype_term=None,
            litter_effects="NA",
            litter_effect_notes="",
            observation_time=104,
            observation_time_units=5,
            observation_time_text="104 weeks",
            data_location="Figure 2B",
            expected_adversity_direction=3,
            response_units="g/100g BW",
            data_type="C",
            variance_type=1,
            confidence_interval=0.95,
            NOEL=1,  # should be the corresponding dose_group_id below or -999
            LOEL=2,  # should be the corresponding dose_group_id below or -999
            FEL=-999,  # should be the corresponding dose_group_id below or -999
            data_reported=True,
            data_extracted=True,
            values_estimated=False,
            monotonicity=8,
            statistical_test="ANOVA + Dunnett's test",
            trend_value=0.0123,
            trend_result=2,
            diagnostic="...",
            power_notes="...",
            results_notes="...",
            endpoint_notes="...",
            effects=["tag1"],
            groups=[
                dict(
                    dose_group_id=0,
                    n=10,
                    incidence=None,
                    response=4.35,
                    variance=0.29,
                    significant=False,
                    significance_level=None,
                ),
                dict(
                    dose_group_id=1,
                    n=10,
                    incidence=None,
                    response=5.81,
                    variance=0.47,
                    significant=False,
                    significance_level=None,
                ),
                dict(
                    dose_group_id=2,
                    n=10,
                    incidence=None,
                    response=7.72,
                    variance=0.63,
                    significant=True,
                    significance_level=0.035,
                ),
            ],
        )
        endpoint = client.animal.create_endpoint(data)
        assert isinstance(endpoint, dict) and endpoint["id"] > 0
        assert len(endpoint["effects"]) == 1
        assert endpoint["effects"][0] == {"name": "tag1", "slug": "tag1"}
        assert len(endpoint["groups"]) == 3

        # test cleanup; remove what we just created
        Experiment.objects.filter(id=experiment["id"]).delete()

    ##########################
    # AssessmentClient tests #
    ##########################

    def test_assessment_public(self):
        client = HawcClient(self.live_server_url)
        response = client.assessment.public()
        assert isinstance(response, list)

    def test_assessment_team_member(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")
        response = client.assessment.team_member()
        assert isinstance(response, list)

    def test_assessment_create_value(self):
        value_data = {
            "assessment_id": 3,
            "evaluation_type": constants.EvaluationType.CANCER,
            "value_type": constants.ValueType.OTHER,
            "uncertainty": constants.UncertaintyChoices.ONE,
            "system": "Hepatic",
            "value": 10,
            "value_unit": "mg",
        }
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")
        response = client.assessment.create_value(value_data)
        assert isinstance(response, dict)

    def test_assessment_create_detail(self):
        details_data = {
            "assessment_id": 3,
            "project_status": constants.Status.SCOPING,
            "peer_review_status": constants.PeerReviewType.NONE,
        }
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")
        response = client.assessment.create_detail(details_data)
        assert isinstance(response, dict)

    def test_assessment_all_values(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("admin@hawcproject.org", "pw")
        response = client.assessment.all_values()
        assert isinstance(response, list)
        assert len(response) == 3

    def test_effect_tag(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("team@hawcproject.org", "pw")
        # test create
        response = client.assessment.effect_tag_create(name="foo", slug="foo")
        assert response == {"name": "foo", "slug": "foo"}

        # test list
        response = client.assessment.effect_tag_list()
        assert response["count"] >= 3

        response = client.assessment.effect_tag_list(name="foo")
        assert response["count"] == 1
        assert response["results"] == [{"name": "foo", "slug": "foo"}]

    ###################
    # EpiClient tests #
    ###################

    def test_epi_data(self):
        client = HawcClient(self.live_server_url)
        response = client.epi.data(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    def test_epi_endpoints(self):
        client = HawcClient(self.live_server_url)
        response = client.epi.endpoints(self.db_keys.assessment_client)
        assert isinstance(response, list)

    def test_epi_metadata(self):
        client = HawcClient(self.live_server_url)
        response = client.epi.metadata(self.db_keys.assessment_client)
        assert isinstance(response, dict)

    def test_epi_crud(self):
        """
        Test all the CRUD methods for epi
        """
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")

        # Study Population #
        # create
        study_pop_name = "test study pop"
        data = dict(
            study=self.db_keys.study_working,
            name=study_pop_name,
            design="CO",
            age_profile="pregnant women",
            source="some source",
            countries=["JP"],
            region="some region",
        )
        study_pop = client.epi.create_study_population(data)

        assert isinstance(study_pop, dict) and study_pop["name"] == study_pop_name
        study_pop_id = study_pop["id"]
        assessment_id = study_pop["study"]["assessment"]

        # read
        assert client.epi.get_study_population(study_pop_id) == study_pop

        study_pop_list = client.epi.get_study_populations(self.db_keys.assessment_working)
        assert isinstance(study_pop_list, pd.DataFrame) and study_pop_list.shape[0] == 1

        # update
        study_pop = client.epi.update_study_population(
            study_pop_id, {"region": "some other region"}
        )
        assert study_pop["region"] == "some other region"

        # Criteria #
        # create
        criteria_desc = "test criteria"
        criteria = client.epi.create_criteria(
            {"description": criteria_desc, "assessment": assessment_id}
        )
        assert isinstance(criteria, dict) and criteria["description"] == criteria_desc
        criteria_id = criteria["id"]

        # read
        assert client.epi.get_criteria(criteria_id)["description"] == criteria_desc

        # update
        updated_criteria = client.epi.update_criteria(
            criteria_id, {"description": "updated test criteria"}
        )
        assert updated_criteria["description"] == "updated test criteria"

        # Exposure #
        exposure_name = "test exposure"
        dose_units = DoseUnits.objects.first()
        exposure = client.epi.create_exposure(
            {
                "name": exposure_name,
                "metric_description": "my description here",
                "metric": "my metric here",
                "analytical_method": "my analytical method here",
                "dtxsid": "DTXSID6026296",
                "inhalation": True,
                "measured": "this is measurement",
                "sampling_period": "sample period here",
                "age_of_exposure": 1,
                "duration": "my duration",
                "exposure_distribution": "my distro",
                "study_population": study_pop_id,
                "metric_units": dose_units.name,
                "n": 9,
                "description": "my desc",
                "central_tendencies": [
                    {
                        "estimate": 14,
                        "estimate_type": 2,
                        "variance": 5.5,
                        "variance_type": "SD",
                        "lower_ci": 4,
                        "upper_ci": 99,
                        "lower_range": 1.2,
                        "upper_range": 1.5,
                        "description": "this is my description",
                    },
                ],
            }
        )
        assert isinstance(exposure, dict) and exposure["name"] == exposure_name
        exposure_id = exposure["id"]

        # read
        assert client.epi.get_exposure(exposure_id)["name"] == exposure_name

        # update
        exposure = client.epi.update_exposure(exposure_id, {"description": "my longer desc"})
        assert exposure["description"] == "my longer desc"

        # Comparison Set #
        # create
        comparison_set_name = "test comparison set"
        comparison_set = client.epi.create_comparison_set(
            {
                "name": comparison_set_name,
                "description": "cs description here",
                "exposure": exposure_id,
                "study_population": study_pop_id,
            }
        )
        assert isinstance(comparison_set, dict) and comparison_set["name"] == comparison_set_name
        comparison_set_id = comparison_set["id"]

        # read
        assert client.epi.get_comparison_set(comparison_set_id) == comparison_set

        # update
        comparison_set = client.epi.update_comparison_set(
            comparison_set_id, {"description": "updated description here"}
        )
        assert comparison_set["description"] == "updated description here"

        # Group #
        # create
        group_name = "test group"
        group = client.epi.create_group(
            {
                "name": group_name,
                "comparison_set": comparison_set_id,
                "group_id": 0,
                "numeric": 1,
                "comparative_name": "compname",
                "sex": "female",
                "eligible_n": 500,
                "invited_n": 250,
                "participant_n": 10,
                "isControl": True,
                "comments": "comments go here",
                "ethnicities": ["Asian"],
            }
        )
        assert isinstance(group, dict) and group["name"] == group_name
        group_id = group["id"]

        # read
        assert client.epi.get_group(group_id)["name"] == group_name

        # update
        group = client.epi.update_group(group_id, {"comments": "updated comments"})
        assert group["comments"] == "updated comments"

        # Group Numerical Description #
        num_desc = "test numerical description"
        nd = client.epi.create_numerical_description(
            {
                "description": num_desc,
                "group": group_id,
                "mean": 2.3,
                "mean_type": "median",
                "variance_type": "gsd",
                "lower_type": 3,
                "upper_type": "UPPER limit",
            }
        )
        assert isinstance(nd, dict) and nd["description"] == num_desc
        nd_id = nd["id"]

        # read
        assert client.epi.get_numerical_description(nd_id)["description"] == num_desc

        # update
        nd = client.epi.update_numerical_description(nd_id, {"mean": 2.4})
        assert nd["mean"] == 2.4

        # Outcome #
        outcome_name = "test outcome"
        outcome = client.epi.create_outcome(
            {
                "name": outcome_name,
                "system": "blood",
                "assessment": assessment_id,
                "diagnostic_description": "this is my description",
                "diagnostic": 5,
                "outcome_n": 2,
                "study_population": study_pop_id,
                "age_of_measurement": "12 years old",
                "summary": "my dsummary",
                "effect": "my effect",
                "effect_subtype": "my subtype",
                "effects": ["tag1"],
            }
        )
        assert isinstance(outcome, dict) and outcome["name"] == outcome_name
        outcome_id = outcome["id"]
        assert len(outcome["effects"]) == 1
        assert outcome["effects"][0] == {"name": "tag1", "slug": "tag1"}

        # read
        assert client.epi.get_outcome(outcome_id)["name"] == outcome_name

        # update
        outcome = client.epi.update_outcome(outcome_id, {"effect": "updated effect"})
        assert outcome["effect"] == "updated effect"

        # Result #
        result_name = "test result"
        result_metric = ResultMetric.objects.first()
        result = client.epi.create_result(
            {
                "name": result_name,
                "outcome": outcome_id,
                "comparison_set": comparison_set_id,
                "metric": result_metric.metric,
                "metric_description": "met desc here",
                "data_location": "Data location here",
                "population_description": "pop desc",
                "dose_response": "monotonic",
                "dose_response_details": "drd",
                "prevalence_incidence": "drd",
                "statistical_power": 2,
                "statistical_power_details": "power_details",
                "statistical_test_results": "stat test results",
                "trend_test": "trend test results",
                "estimate_type": "point",
                "variance_type": 4,
                "ci_units": 0.95,
                "factors_applied": ["birth order"],
                "factors_considered": ["dynamic factor", "study center"],
                "comments": "comments go here",
                "resulttags": ["tag2"],
            }
        )
        assert isinstance(result, dict) and result["name"] == result_name
        result_id = result["id"]
        assert len(result["resulttags"]) == 1
        assert result["resulttags"][0] == {"name": "tag2", "slug": "tag2"}

        # read
        assert client.epi.get_result(result_id)["name"] == result_name

        # update
        result = client.epi.update_result(
            result_id, {"metric_description": "updated met desc here"}
        )
        assert result["metric_description"] == "updated met desc here"

        # Group Result #
        gr_pval = 0.432
        group_result = client.epi.create_group_result(
            {
                "result": result_id,
                "n": 50,
                "main_finding_support": "inconclusive",
                "p_value_qualifier": "<",
                "p_value": gr_pval,
                "group": group_id,
                "estimate": 12,
                "variance": 15,
                "lower_ci": 1,
                "upper_ci": 9,
                "lower_range": 5,
                "upper_range": 7,
                "is_main_finding": False,
            }
        )
        assert isinstance(group_result, dict) and group_result["p_value"] == gr_pval
        group_result_id = group_result["id"]

        # read
        assert client.epi.get_group_result(group_result_id)["p_value"] == gr_pval

        # update
        group_result = client.epi.update_group_result(group_result_id, {"n": 51})
        assert group_result["n"] == 51

        # test cleanup; remove what we just created
        assert client.epi.delete_criteria(criteria_id).status_code == 204
        assert client.epi.delete_group_result(group_result_id).status_code == 204
        assert client.epi.delete_result(result_id).status_code == 204
        assert client.epi.delete_outcome(outcome_id).status_code == 204
        assert client.epi.delete_numerical_description(nd_id).status_code == 204
        assert client.epi.delete_group(group_id).status_code == 204
        assert client.epi.delete_comparison_set(comparison_set_id).status_code == 204
        assert client.epi.delete_exposure(exposure_id).status_code == 204
        assert client.epi.delete_study_population(study_pop_id).status_code == 204

    #####################
    # EpiV2Client tests #
    #####################

    def test_epiv2_crud(self):
        """
        Test all the create/read/update/delete methods for epi v2
        """

        def common_result_check(result, payload, key):
            assert isinstance(result, dict) and result[key] == payload[key]

        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")
        epi_client = client.epiv2

        ###
        ### design
        ###
        design_payload = {
            "study_id": self.db_keys.study_working,
            "summary": "D summary",
            "study_name": "D study name",
            "study_design": "Cohort",
            "source": "General Population",
            "age_profile": ["Adults"],
            "age_description": "D age",
            "sex": "Male and Female",
            "countries": ["JP"],
            "race": "D race",
            "participant_n": 99,
            "criteria": "D criteria",
            "susceptibility": "D susceptibility",
            "region": "D region",
            "years_enrolled": "D years enrolled",
            "years_followup": "D years followup",
            "comments": "D comments",
        }

        # create
        design_result = epi_client.create_design(design_payload)

        common_result_check(design_result, design_payload, "summary")

        design_id = design_result["id"]

        # update
        design_payload["summary"] = "modified summary"
        design_result = epi_client.update_design(design_id, design_payload)
        common_result_check(design_result, design_payload, "summary")

        # read
        design_result = epi_client.get_design(design_id)
        common_result_check(design_result, design_payload, "summary")

        # list
        study = Study.objects.get(id=self.db_keys.study_working)
        list_by_assessment_result = epi_client.get_designs_for_assessment(
            assessment_id=study.assessment_id
        )
        list_by_study_result = epi_client.get_designs_for_study(
            assessment_id=study.assessment_id, study_id=study.id
        )
        assert (
            list_by_study_result["count"].tolist()[0]
            == list_by_assessment_result["count"].tolist()[0]
        )

        ###
        ### chemical
        ###
        chemical_payload = {
            "design": design_id,
            "name": "C name",
            "dsstox_id": "DTXSID6026296",
        }

        # create
        chemical_result = epi_client.create_chemical(chemical_payload)
        common_result_check(chemical_result, chemical_payload, "name")

        assert chemical_result["dsstox"]["dtxsid"] == chemical_payload["dsstox_id"]
        chemical_id = chemical_result["id"]

        # update
        chemical_payload["name"] = "modified name"
        chemical_result = epi_client.update_chemical(chemical_id, chemical_payload)
        common_result_check(chemical_result, chemical_payload, "name")

        # read
        chemical_result = epi_client.get_chemical(chemical_id)
        common_result_check(chemical_result, chemical_payload, "name")

        ###
        ### exposure (measurement)
        ###
        exposure_payload = {
            "design": design_id,
            "name": "E name",
            "measurement_type": ["Biomonitoring", "Air"],
            "biomonitoring_matrix": "BLP",
            "biomonitoring_source": "PT",
            "measurement_timing": "E timing",
            "exposure_route": "IH",
            "measurement_method": "E meas method",
            "comments": "E comments",
        }

        # create
        exposure_result = epi_client.create_exposure(exposure_payload)
        common_result_check(exposure_result, exposure_payload, "name")

        exposure_id = exposure_result["id"]

        # update
        exposure_payload["name"] = "modified name"
        exposure_result = epi_client.update_exposure(exposure_id, exposure_payload)
        common_result_check(exposure_result, exposure_payload, "name")

        # read
        exposure_result = epi_client.get_exposure(exposure_id)
        common_result_check(exposure_result, exposure_payload, "name")

        ###
        ### exposure level
        ###
        exposure_level_payload = {
            "design": design_id,
            "name": "EL name",
            "chemical_id": chemical_id,
            "exposure_measurement_id": exposure_id,
            "sub_population": "EL subpop",
            "median": 1.1,
            "mean": 1.2,
            "variance": 1.3,
            "variance_type": "SD",
            "units": "EL units",
            "ci_lcl": "1.4",
            "percentile_25": "1.5",
            "percentile_75": "1.6",
            "ci_ucl": "1.7",
            "ci_type": "Rng",
            "negligible_exposure": "EL neg expo",
            "data_location": "EL dataloc",
            "comments": "EL comments",
        }

        # create
        exposure_level_result = epi_client.create_exposure_level(exposure_level_payload)
        common_result_check(exposure_level_result, exposure_level_payload, "name")

        exposure_level_id = exposure_level_result["id"]

        # update
        exposure_level_payload["name"] = "modified name"
        exposure_level_result = epi_client.update_exposure_level(
            exposure_level_id, exposure_level_payload
        )
        common_result_check(exposure_level_result, exposure_level_payload, "name")

        # read
        exposure_level_result = epi_client.get_exposure_level(exposure_level_id)
        common_result_check(exposure_level_result, exposure_level_payload, "name")

        ###
        ### outcome
        ###
        outcome_payload = {
            "design": design_id,
            "system": "Reproductive",
            "effect": "O effect",
            "effect_detail": "O detail",
            "endpoint": "O endpoint",
            "comments": "O comments",
        }

        # create
        outcome_result = epi_client.create_outcome(outcome_payload)
        common_result_check(outcome_result, outcome_payload, "effect")

        outcome_id = outcome_result["id"]

        # update
        outcome_payload["effect"] = "modified effect"
        outcome_result = epi_client.update_outcome(outcome_id, outcome_payload)
        common_result_check(outcome_result, outcome_payload, "effect")

        # read
        outcome_result = epi_client.get_outcome(outcome_id)
        common_result_check(outcome_result, outcome_payload, "effect")

        ###
        ### adjustment factor
        ###
        adjustment_factor_payload = {
            "design": design_id,
            "name": "AF name",
            "description": "AF description",
            "comments": "AF comments",
        }

        # create
        adjustment_factor_result = epi_client.create_adjustment_factor(adjustment_factor_payload)
        common_result_check(adjustment_factor_result, adjustment_factor_payload, "name")

        adj_factor_id = adjustment_factor_result["id"]

        # update
        adjustment_factor_payload["name"] = "modified name"
        adjustment_factor_result = epi_client.update_adjustment_factor(
            adj_factor_id, adjustment_factor_payload
        )
        common_result_check(adjustment_factor_result, adjustment_factor_payload, "name")

        # read
        adjustment_factor_result = epi_client.get_adjustment_factor(adj_factor_id)
        common_result_check(adjustment_factor_result, adjustment_factor_payload, "name")

        ###
        ### data extraction
        ###
        data_extraction_payload = {
            "design": design_id,
            "outcome_id": outcome_id,
            "exposure_level_id": exposure_level_id,
            "sub_population": "DE subpop",
            "outcome_measurement_timing": "DE meas timing",
            "effect_estimate_type": "Absolute Risk %",
            "effect_estimate": 1.1,
            "ci_lcl": 1.2,
            "ci_ucl": 1.3,
            "ci_type": "Rng",
            "units": "DE units",
            "variance_type": "SD",
            "variance": 1.4,
            "n": 99,
            "p_value": "DE pval",
            "significant": "No",
            "group": "DE group",
            "exposure_rank": 1,
            "exposure_transform": "DE expo transform",
            "outcome_transform": "DE outcome transform",
            "factors": adj_factor_id,
            "confidence": "DE confidence",
            "adverse_direction": "up",
            "data_location": "DE loc",
            "effect_description": "DE effect desc",
            "statistical_method": "DE stat method",
            "comments": "DE comments",
        }

        # create
        data_extraction_result = epi_client.create_data_extraction(data_extraction_payload)
        common_result_check(data_extraction_result, data_extraction_payload, "comments")

        data_extraction_id = data_extraction_result["id"]

        # update
        data_extraction_payload["comments"] = "modified comments"
        data_extraction_result = epi_client.update_data_extraction(
            data_extraction_id, data_extraction_payload
        )
        common_result_check(data_extraction_result, data_extraction_payload, "comments")

        # read
        data_extraction_result = epi_client.get_data_extraction(data_extraction_id)
        common_result_check(data_extraction_result, data_extraction_payload, "comments")

        ###
        ### all
        ###
        # delete
        deletions = (
            (data_extraction_id, epi_client.delete_data_extraction, epiv2models.DataExtraction),
            (exposure_level_id, epi_client.delete_exposure_level, epiv2models.ExposureLevel),
            (outcome_id, epi_client.delete_outcome, epiv2models.Outcome),
            (adj_factor_id, epi_client.delete_adjustment_factor, epiv2models.AdjustmentFactor),
            (chemical_id, epi_client.delete_chemical, epiv2models.Chemical),
            (exposure_id, epi_client.delete_exposure, epiv2models.Exposure),
            (design_id, epi_client.delete_design, epiv2models.Design),
        )

        for primary_key, client_delete_method, model_class in deletions:
            deletion_response = client_delete_method(primary_key)
            assert deletion_response.status_code == 204
            assert not model_class.objects.filter(id=primary_key).exists()

    def test_epiv2_metadata(self):
        """
        Test metadata retrieval for epi v2
        """
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")
        epi_client = client.epiv2

        metadata = epi_client.metadata()
        assert isinstance(metadata, dict)

        # spotcheck a few items in the returned metadata
        things_to_check = [
            {"model": "study", "props": {"coi_reported": studyconstants.CoiReported}},
            {
                "model": "design",
                "props": {
                    "study_design": epiv2constants.StudyDesign,
                    "source": epiv2constants.Source,
                },
            },
            {
                "model": "exposure_level",
                "props": {
                    "variance_type": epiv2constants.VarianceType,
                    "ci_type": epiv2constants.ConfidenceIntervalType,
                },
            },
        ]

        for thing_to_check in things_to_check:
            model_name = thing_to_check.get("model")
            assert model_name in metadata
            metadata_details = metadata.get(model_name)
            props = thing_to_check.get("props")
            for prop_name in props:
                assert prop_name in metadata_details
                metadata_vals = metadata_details.get(prop_name)
                legal_vals_to_check = props.get(prop_name)

                for legal_val_to_check in legal_vals_to_check:
                    assert str(legal_val_to_check.value) in metadata_vals
                    metadata_display = metadata_vals.get(str(legal_val_to_check.value))
                    assert metadata_display == legal_val_to_check.label

    def test_epiv2_data_export(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")
        epi_client = client.epiv2

        df = epi_client.data(
            assessment_id=self.db_keys.assessment_working, retrieve_unpublished_data=True
        )
        assert isinstance(df, pd.DataFrame) and df.shape == (12, 116)

    #######################
    # EpiMetaClient tests #
    #######################

    def test_epimeta_data(self):
        client = HawcClient(self.live_server_url)
        response = client.epimeta.data(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    #######################
    # InvitroClient tests #
    #######################

    def test_invitro_data(self):
        client = HawcClient(self.live_server_url)
        response = client.invitro.data(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    ##########################
    # LiteratureClient tests #
    ##########################

    @pytest.mark.vcr
    def test_lit_import_hero(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")
        hero_ids = [
            2199697,
            5353200,
            595055,
            5176411,
            5920377,
        ]
        response = client.lit.import_hero(
            assessment_id=self.db_keys.assessment_client,
            title="HERO import",
            description="Description",
            ids=hero_ids,
        )
        assert isinstance(response, dict)

    @pytest.mark.vcr
    def test_lit_import_pubmed(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")
        pubmed_ids = [10357793, 20358181, 6355494, 8998951, 3383337]
        response = client.lit.import_pubmed(
            assessment_id=self.db_keys.assessment_client,
            title="PubMed import",
            description="Description",
            ids=pubmed_ids,
        )
        assert isinstance(response, dict)

    def test_lit_tags(self):
        client = HawcClient(self.live_server_url)
        response = client.lit.tags(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    def test_get_tagtree(self):
        client = HawcClient(self.live_server_url)
        response = client.lit.get_tagtree(self.db_keys.assessment_client)
        assert isinstance(response, list)

    def test_clone_tagtree(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")
        response = client.lit.clone_tagtree(
            self.db_keys.assessment_final, self.db_keys.assessment_client
        )
        assert isinstance(response, list)

    def test_update_tagtree(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")

        updates = [
            {"data": {"name": "set via client"}},
            {"data": {"name": "Client Slug", "slug": "sluggo"}},
            {"data": {"name": "tree"}, "children": [{"data": {"name": "child element"}}]},
        ]

        response = client.lit.update_tagtree(self.db_keys.assessment_client, updates)
        assert isinstance(response, list)

    def test_lit_reference_tags(self):
        client = HawcClient(self.live_server_url)
        response = client.lit.reference_tags(self.db_keys.assessment_final)
        assert isinstance(response, pd.DataFrame)

    def test_lit_import_reference_tags(self):
        csv = "reference_id,tag_id\n1,2"
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")
        response = client.lit.import_reference_tags(
            assessment_id=self.db_keys.assessment_working, csv=csv
        )
        assert isinstance(response, pd.DataFrame)

    def test_lit_reference_ids(self):
        client = HawcClient(self.live_server_url)
        response = client.lit.reference_ids(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    def test_lit_references(self):
        client = HawcClient(self.live_server_url)
        response = client.lit.references(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    def test_lit_reference_user_tags(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")
        response = client.lit.reference_user_tags(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    def test_lit_reference(self):
        # get request
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")

        # imported from `test_lit_import_hero` above; test test must run for this one to run :/
        reference_id = Reference.objects.get(identifiers__unique_id="2199697").id

        ref = client.lit.reference(reference_id)
        assert ref["id"] == reference_id

        # update request
        updated_title = "client test"
        ref = client.lit.update_reference(reference_id, title=updated_title)
        assert ref["title"] == updated_title

        # delete request
        ref = client.lit.reference(reference_id)
        assert ref["id"] == reference_id
        response = client.lit.delete_reference(reference_id)
        assert response is None

        # reference retrieval returns 404
        with pytest.raises(HawcClientException) as err:
            client.lit.reference(reference_id)

        assert err.value.status_code == 404

    @pytest.mark.vcr
    def test_update_references_from_hero(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")

        assessment_id = self.db_keys.assessment_working

        references = Reference.objects.filter(assessment_id=assessment_id)

        assert references.filter(title="").count() > 0

        response = client.lit.update_references_from_hero(assessment_id)
        assert response is None

        # Reference fields should now be set with HERO metadata
        assert references.filter(title="").count() == 0

    @pytest.mark.vcr
    def test_replace_hero(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")

        reference = Reference.objects.get(id=self.db_keys.reference_linked)
        assessment_id = reference.assessment_id
        replace = [[reference.id, 1037739]]

        response = client.lit.replace_hero(assessment_id, replace)
        assert response is None

        # Make sure reference fields have been updated
        updated_reference = Reference.objects.get(id=self.db_keys.reference_linked)
        assert (
            updated_reference.title
            == "Observation of Methanol Behavior in Fuel Cells In Situ by NMR Spectroscopy"
        )
        # Make sure HERO identifier has been replaced
        updated_hero = updated_reference.identifiers.get(database=2)
        assert updated_hero.unique_id == "1037739"

    def test_tags(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")

        # create
        data = {"assessment_id": self.db_keys.assessment_working, "name": "Test", "parent": 28}
        instance = client.lit.create_tag(data)
        assert instance["name"] == "Test"

        # update
        data = {"name": "Test2"}
        tag_id = instance["id"]
        instance = client.lit.update_tag(tag_id, data)
        assert instance["name"] == "Test2"

        # delete
        response = client.lit.delete_tag(tag_id)
        assert response.status_code == 204

        # move tag
        tags = ReferenceFilterTag.get_assessment_qs(3)
        tag = tags.get(name="Tier I")

        qs = tags.get(name="Exclusion").get_descendants().values_list("name", flat=True)
        assert list(qs) == ["Tier I", "Tier II", "Tier III"]

        response = client.lit.move_tag(tag.id, new_index=2).json()
        assert response["status"] is True

        qs = tags.get(name="Exclusion").get_descendants().values_list("name", flat=True)
        assert list(qs) == ["Tier II", "Tier III", "Tier I"]

    ##########################
    # RiskOfBiasClient tests #
    ##########################

    def test_riskofbias_export(self):
        client = HawcClient(self.live_server_url)
        response = client.riskofbias.export(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    def test_riskofbias_full_export(self):
        client = HawcClient(self.live_server_url)

        # permission denied
        with pytest.raises(HawcClientException) as err:
            client.riskofbias.full_export(self.db_keys.assessment_client)
            assert err.status_code == 403

        # successful response
        client.authenticate("team@hawcproject.org", "pw")
        response = client.riskofbias.full_export(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    def test_riskofbias_create(self):
        """
        Test all the create methods.  This only checks the happy-path and confirms that the client
        methods work as intended.
        """
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")

        scores = [
            {
                "metric_id": metric_id,
                "is_default": True,
                "label": "",
                "score": 16,
                "bias_direction": 1,
                "notes": "<p>more custom notes</p>",
            }
            for metric_id in self.db_keys.riskofbias_assessment_working_metric_ids
        ]

        rob = client.riskofbias.create(
            study_id=self.db_keys.study_working,
            author_id=self.db_keys.pm_user_id,
            active=False,
            final=True,
            scores=scores,
        )

        assert isinstance(rob, dict) and rob["id"] > 0

    def test_riskofbias_metrics(self):
        client = HawcClient(self.live_server_url)
        df = client.riskofbias.metrics(self.db_keys.assessment_client)
        assert isinstance(df, pd.DataFrame) and df.shape == (11, 15)

    def test_riskofbias_compare_metrics(self):
        client = HawcClient(self.live_server_url)
        df_src, df_dst = client.riskofbias.compare_metrics(
            self.db_keys.assessment_client, self.db_keys.assessment_final
        )
        assert isinstance(df_src, pd.DataFrame) and df_src.shape == (11, 19)
        assert isinstance(df_dst, pd.DataFrame) and df_dst.shape == (2, 17)
        assert all(
            col in df_src.columns for col in ["matched_key", "matched_score", "matched_text"]
        )

    def test_riskofbias_reviews(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("team@hawcproject.org", "pw")
        response = client.riskofbias.reviews(self.db_keys.assessment_final)
        assert isinstance(response, list) and len(response) > 0
        assert len(response) == 6
        assert response[0]["scores"][0]["score_symbol"] == "++"

    def test_riskofbias_final_reviews(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("team@hawcproject.org", "pw")
        response = client.riskofbias.final_reviews(self.db_keys.assessment_final)
        assert isinstance(response, list) and len(response) > 0
        assert len(response) > 0
        assert all(review["final"] is True for review in response)

    #######################
    # SummaryClient tests #
    #######################

    def test_summary_visual_list(self):
        client = HawcClient(self.live_server_url)
        response = client.summary.visual_list(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    def test_summary_crud(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("admin@hawcproject.org", "pw")
        # Visual #
        # create
        visual_title = "barchart-2"
        visual_data = {
            "title": visual_title,
            "slug": "barchart-2",
            "visual_type": 3,
            "evidence_type": 0,
            "settings": json.loads(
                '{"title":"Title","xAxisLabel":"Percent of studies","yAxisLabel":"","plot_width":400,"row_height":30,"padding_top":40,"padding_right":300,"padding_bottom":40,"padding_left":70,"show_values":true,"included_metrics":[14,15],"show_legend":true,"show_na_legend":true,"legend_x":574,"legend_y":10}'
            ),
            "assessment": self.db_keys.assessment_working,
            "prefilters": {},
            "caption": "<p>caption</p>",
            "published": True,
            "sort_order": "short_citation",
            "endpoints": [],
            "studies": [],
        }
        visual = client.summary.create_visual(visual_data)
        assert isinstance(visual, dict) and visual["title"] == visual_title
        visual_id = visual["id"]

        # read
        visual = client.summary.get_visual(visual_id)
        assert visual["title"] == visual_title

        # update
        visual_data["published"] = False
        visual = client.summary.update_visual(visual_id, visual_data)
        assert visual["published"] is False

        # Data Pivot #
        # read
        slug = "animal-bioassay-data-pivot-endpoint"
        dp_id = DataPivot.objects.get(slug=slug).pk
        dp = client.summary.get_datapivot(dp_id)
        assert dp["slug"] == slug

        # create
        new_slug = f"{slug}-2"
        new_dp_data = dp.copy()
        new_dp_data["slug"] = new_slug
        new_dp_data.pop("id")
        new_dp = client.summary.create_datapivot(new_dp_data)
        assert new_dp["slug"] == new_slug
        new_dp_id = new_dp["id"]

        # update
        assert new_dp_data["published"] is True
        new_dp_data["published"] = False
        new_dp = client.summary.update_datapivot(new_dp_id, new_dp_data)
        assert new_dp["published"] is False

        # Delete all the objects we created
        assert client.summary.delete_visual(visual_id) is None
        assert client.summary.delete_datapivot(new_dp_id) is None

    #####################
    # StudyClient tests #
    #####################

    def test_study_create(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")
        response = client.study.create(self.db_keys.reference_unlinked)
        assert isinstance(response, dict)

    def test_study_list(self):
        client = HawcClient(self.live_server_url)
        df = client.study.studies(self.db_keys.assessment_client)
        assert isinstance(df, pd.DataFrame) and df.shape == (1, 29)
        assert df.short_citation.values == ["Yoshida R and Ogawa Y 2000"]

    def test_study_create_from_identifier(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")
        response = client.study.create_from_identifier(
            db_type="HERO", db_id=2199697, assessment_id=self.db_keys.assessment_client
        )
        assert isinstance(response, dict)
