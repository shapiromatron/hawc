import pandas as pd
import pytest
from django.core.cache import cache
from django.test import LiveServerTestCase, TestCase

from hawc_client import BaseClient, HawcClient


@pytest.mark.usefixtures("set_db_keys")
class TestClient(LiveServerTestCase, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

    def test_animal_data_summary(self):
        client = HawcClient(self.live_server_url)
        response = client.animal.data_summary(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)

    def test_animal_endpoints(self):
        client = HawcClient(self.live_server_url)
        response = client.animal.endpoints(self.db_keys.assessment_client)
        assert isinstance(response, list)

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
        client.authenticate("pm@pm.com", "pw")
        hero_ids = [
            10357793,
            20358181,
            6355494,
            8998951,
            3383337,
            12209194,
            6677511,
            11995694,
            1632818,
            12215663,
            3180084,
            14727734,
            23625783,
            11246142,
            10485824,
            3709451,
            2877511,
            6143560,
            3934796,
            8761421,
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
        csv = "reference_id,tag_id\n2,14"
        client = HawcClient(self.live_server_url)
        client.authenticate("pm@pm.com", "pw")
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

    #######################
    # SummaryClient tests #
    #######################

    def test_summary_visual_list(self):
        client = HawcClient(self.live_server_url)
        response = client.summary.visual_list(self.db_keys.assessment_client)
        assert isinstance(response, pd.DataFrame)
