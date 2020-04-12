import pytest
from hawc_client import HawcClient
import pandas as pd


@pytest.mark.usefixtures("load_test_db")
def test_data(live_server, db_keys):
    client = HawcClient(live_server.url)
    response = client.epimeta.data(db_keys.assessment_client)
    assert type(response) is pd.DataFrame
