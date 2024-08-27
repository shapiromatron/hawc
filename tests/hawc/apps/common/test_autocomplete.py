import pytest
from django.test.client import Client


@pytest.mark.django_db
def test_null_query():
    # check that null string, q=\0 or q=%00 is cleaned
    url = "/autocomplete/assessment-dsstoxautocomplete/"
    client = Client()
    resp = client.get(url + "?q=\0")
    assert resp.status_code == 200


@pytest.mark.django_db
def test_400_errors():
    # check that bad requests are caught properly
    url = "/autocomplete/study-studyautocomplete/?assessment_id=1&bioassay=bKRc26YM:%20h4vqyNto"
    client = Client()
    resp = client.get(url)
    assert resp.status_code == 400

    url = "/autocomplete/animal-endpointautocomplete/?animal_group__experiment__study__assessment_id=499&create=false&field=%3C!--&q=e"
    resp = client.get(url)
    assert resp.status_code == 400
