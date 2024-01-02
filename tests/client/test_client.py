from io import BytesIO

import pandas as pd
import pytest
from django.core.cache import cache
from django.test import LiveServerTestCase, TestCase

from hawc.apps.animal.models import Experiment
from hawc.apps.assessment import constants
from hawc.apps.assessment.models import DoseUnits, Strain
from hawc.apps.epi.models import (
    ComparisonSet,
    Criteria,
    Exposure,
    Group,
    GroupNumericalDescriptions,
    GroupResult,
    Outcome,
    Result,
    ResultMetric,
    StudyPopulation,
)
from hawc.apps.lit.models import Reference
from hawc.apps.myuser.models import HAWCUser
from hawc_client import BaseClient, HawcClient, HawcClientException, InteractiveHawcClient


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

        # test cleanup; remove what we just created
        Experiment.objects.filter(id=experiment["id"]).delete()

    ##########################
    # AssessmentClient tests #
    ##########################

    def test_assessment_public(self):
        client = HawcClient(self.live_server_url)
        response = client.assessment.public()
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

    def test_epi_create(self):
        """
        Test all the create methods for epi
        """
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")

        # study population
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

        # criteria
        criteria_desc = "test criteria"
        criteria = client.epi.create_criteria(
            {"description": criteria_desc, "assessment": assessment_id}
        )
        assert isinstance(criteria, dict) and criteria["description"] == criteria_desc
        criteria_id = criteria["id"]

        # exposure
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

        # comparison set
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

        # group
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

        # group numerical description
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

        # outcome
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
            }
        )
        assert isinstance(outcome, dict) and outcome["name"] == outcome_name
        outcome_id = outcome["id"]

        # result
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
            }
        )
        assert isinstance(result, dict) and result["name"] == result_name
        result_id = result["id"]

        # group result
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

        # test cleanup; remove what we just created
        Criteria.objects.filter(id=criteria_id).delete()
        GroupResult.objects.filter(id=group_result_id).delete()
        Result.objects.filter(id=result_id).delete()
        Outcome.objects.filter(id=outcome_id).delete()
        GroupNumericalDescriptions.objects.filter(id=nd_id).delete()
        Group.objects.filter(id=group_id).delete()
        ComparisonSet.objects.filter(id=comparison_set_id).delete()
        Exposure.objects.filter(id=exposure_id).delete()
        StudyPopulation.objects.filter(id=study_pop_id).delete()

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
        response = client.riskofbias.reviews(self.db_keys.assessment_final)
        assert isinstance(response, list) and len(response) > 0
        assert len(response) == 6
        assert response[0]["scores"][0]["score_symbol"] == "++"

    #######################
    # SummaryClient tests #
    #######################

    def test_summary_visual_list(self):
        client = HawcClient(self.live_server_url)
        response = client.summary.visual_list(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    def test_summary_download_visual(self):
        client = HawcClient(self.live_server_url)
        with InteractiveHawcClient(client) as iclient:
            result = iclient.download_visual(1)
        assert isinstance(result, BytesIO)

    def test_summary_download_data_pivot(self):
        client = HawcClient(self.live_server_url)
        with InteractiveHawcClient(client) as iclient:
            result = iclient.download_data_pivot(1)
        assert isinstance(result, BytesIO)

    def test_download_all_visuals(self):
        client = HawcClient(self.live_server_url)
        token = HAWCUser.objects.get(email="pm@hawcproject.org").get_api_token().key
        client.set_authentication_token(token, login=False)
        results = client.summary.download_all_visuals(self.db_keys.assessment_working)
        assert len(results) == 2
        for result in results:
            assert isinstance(result["png"], BytesIO)

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
