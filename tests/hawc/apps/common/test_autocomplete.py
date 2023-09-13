import pytest
from django.test.client import Client


@pytest.mark.django_db
def test_null_query():
    # check that null string, q=\0 or q=%00 is cleaned
    url = "/autocomplete/assessment-dsstoxautocomplete/"
    client = Client()
    resp = client.get(url + "?q=\0")
    assert resp.status_code == 200
