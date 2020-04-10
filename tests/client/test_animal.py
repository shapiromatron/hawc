from hawc_client import HawcClient


def test_data(live_server, db_keys):
    client = HawcClient(live_server.url)
    response = client.animal.data(db_keys.assessment_final)
    assert response is not None


def test_data_summary(live_server, db_keys):
    client = HawcClient(live_server.url)
    response = client.animal.data_summary(db_keys.assessment_final)
    assert response is not None


def test_endpoints(live_server, db_keys):
    client = HawcClient(live_server.url)
    response = client.animal.endpoints(db_keys.assessment_final)
    assert response is not None
