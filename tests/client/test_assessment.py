from hawc_client import HawcClient


def test_public(live_server):
    client = HawcClient(live_server.url)
    response = client.assessment.public()
    assert response is not None


def test_bioassay_ml_dataset(live_server):
    client = HawcClient(live_server.url)
    response = client.assessment.bioassay_ml_dataset()
    assert response is not None
