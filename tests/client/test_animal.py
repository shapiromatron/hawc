import pandas as pd
import pytest

from hawc_client import HawcClient


@pytest.mark.usefixtures("load_test_db")
def test_data(live_server, db_keys):
    client = HawcClient(live_server.url)
    response = client.animal.data(db_keys.assessment_client)
    assert type(response) is pd.DataFrame


@pytest.mark.usefixtures("load_test_db")
def test_data_summary(live_server, db_keys):
    client = HawcClient(live_server.url)
    response = client.animal.data_summary(db_keys.assessment_client)
    assert type(response) is pd.DataFrame


@pytest.mark.usefixtures("load_test_db")
def test_endpoints(live_server, db_keys):
    client = HawcClient(live_server.url)
    response = client.animal.endpoints(db_keys.assessment_client)
    assert type(response) is list
