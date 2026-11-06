import pytest
from django.test import LiveServerTestCase, TestCase

from hawc_client import HawcClient


@pytest.mark.usefixtures("set_db_keys")
class TestVocabClient(LiveServerTestCase, TestCase):
    """Exercise vocabulary client methods against the live Django server."""

    def setUp(self):
        self.client = HawcClient(self.live_server_url)
        self.client.authenticate("admin@hawcproject.org", "pw")

    def test_bulk_create_posts_terms_and_returns_json(self):
        result = self.client.vocab.bulk_create([{"uid": 9100, "name": "system", "type": 1}])

        assert result[0]["uid"] == 9100
        assert result[0]["name"] == "system"
        assert "id" in result[0]

    def test_bulk_update_patches_terms_and_returns_json(self):
        created = self.client.vocab.bulk_create([{"uid": 9101, "name": "before", "type": 1}])[0]

        result = self.client.vocab.bulk_update([{"id": created["id"], "name": "updated"}])

        assert result[0]["id"] == created["id"]
        assert result[0]["name"] == "updated"

    def test_uids_gets_id_uid_pairs(self):
        created = self.client.vocab.bulk_create([{"uid": 9102, "name": "uids", "type": 1}])[0]

        result = self.client.vocab.uids()

        assert [created["id"], 9102] in result
