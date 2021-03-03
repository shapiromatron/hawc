import pandas as pd
import pytest
from django.core.cache import cache
from django.test import LiveServerTestCase, TestCase

from hawc.apps.animal.models import Experiment
from hawc.apps.assessment.models import Strain
from hawc.apps.lit.models import Reference
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
        response = client.animal.endpoints(self.db_keys.assessment_client)
        assert isinstance(response, list)

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
            system="Hepatic",
            organ="Liver",
            effect="Organ weight",
            effect_subtype="Relative weight",
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

    def test_assessment_bioassay_ml_dataset(self):
        client = HawcClient(self.live_server_url)
        response = client.assessment.bioassay_ml_dataset()
        assert isinstance(response, pd.DataFrame)

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
            title="Title",
            description="Description",
            ids=hero_ids,
        )
        assert isinstance(response, dict)

    def test_lit_tags(self):
        client = HawcClient(self.live_server_url)
        response = client.lit.tags(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    def test_lit_reference_tags(self):
        client = HawcClient(self.live_server_url)
        response = client.lit.reference_tags(self.db_keys.assessment_final)
        assert isinstance(response, pd.DataFrame)

    def test_lit_import_reference_tags(self):
        csv = "reference_id,tag_id\n5,14"
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")
        response = client.lit.import_reference_tags(
            assessment_id=self.db_keys.assessment_final, csv=csv
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

    def test_riskofbias_data(self):
        client = HawcClient(self.live_server_url)
        response = client.riskofbias.data(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    def test_riskofbias_full_data(self):
        client = HawcClient(self.live_server_url)
        response = client.riskofbias.full_data(self.db_keys.assessment_client)
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

    #######################
    # SummaryClient tests #
    #######################

    def test_summary_visual_list(self):
        client = HawcClient(self.live_server_url)
        response = client.summary.visual_list(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    #####################
    # StudyClient tests #
    #####################

    def test_study_create(self):
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@hawcproject.org", "pw")
        response = client.study.create(self.db_keys.reference_unlinked)
        assert isinstance(response, dict)
