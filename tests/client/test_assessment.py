import pandas as pd
import pytest

from hawc_client import HawcClient


@pytest.mark.usefixtures("load_test_db")
def test_public(live_server):
    client = HawcClient(live_server.url)
    response = client.assessment.public()
    assert type(response) is list


@pytest.mark.usefixtures("load_test_db")
def test_bioassay_ml_dataset(live_server):
    client = HawcClient(live_server.url)
    response = client.assessment.bioassay_ml_dataset()
    assert type(response) is pd.DataFrame
