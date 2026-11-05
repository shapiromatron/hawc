from hawc_client.vocab import VocabClient


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


class FakeSession:
    root_url = "https://hawc.example"

    def __init__(self):
        self.calls = []

    def post(self, url, payload):
        self.calls.append(("post", url, payload))
        return FakeResponse([{"id": 1, **payload[0]}])

    def patch(self, url, payload):
        self.calls.append(("patch", url, payload))
        return FakeResponse([{"id": 1, **payload[0]}])

    def get(self, url):
        self.calls.append(("get", url))
        return FakeResponse([[1, 100]])


def test_bulk_create_posts_terms_and_returns_json():
    session = FakeSession()
    terms = [{"uid": 100, "name": "system"}]

    result = VocabClient(session).bulk_create(terms)

    assert result == [{"id": 1, "uid": 100, "name": "system"}]
    assert session.calls == [("post", "https://hawc.example/vocab/api/term/bulk-create/", terms)]


def test_bulk_update_patches_terms_and_returns_json():
    session = FakeSession()
    terms = [{"id": 1, "name": "updated"}]

    result = VocabClient(session).bulk_update(terms)

    assert result == [{"id": 1, "name": "updated"}]
    assert session.calls == [("patch", "https://hawc.example/vocab/api/term/bulk-update/", terms)]


def test_uids_gets_id_uid_pairs():
    session = FakeSession()

    result = VocabClient(session).uids()

    assert result == [[1, 100]]
    assert session.calls == [("get", "https://hawc.example/vocab/api/term/uids/")]
