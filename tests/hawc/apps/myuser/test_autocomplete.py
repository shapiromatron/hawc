import pytest

from ..test_utils import get_client


@pytest.mark.django_db
def test_autocomplete():
    url = "/autocomplete/myuser-userautocomplete/?q=team"
    client = get_client()
    resp = client.get(url)
    assert resp.status_code == 403

    client = get_client("pm")
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.json()["results"] == [
        {"id": "3", "text": "Team Member", "selected_text": "Team Member"}
    ]
