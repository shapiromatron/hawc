import pytest
import requests
from requests.adapters import HTTPAdapter


@pytest.fixture
def build_response():
    """Factory building a `requests.Response` without making a network request."""

    def factory(text: str = "", status_code: int = 200) -> requests.Response:
        response = requests.Response()
        response.status_code = status_code
        response.encoding = "utf-8"
        response._content = text.encode("utf-8")
        return response

    return factory


@pytest.fixture
def build_session():
    """Factory building a`requests.Session` which replays outcomes instead of using a network."""

    def factory(*outcomes) -> requests.Session:
        session = requests.Session()
        adapter = QueuedAdapter(*outcomes)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    return factory


class QueuedAdapter(HTTPAdapter):
    """A transport adapter which returns (or raises) queued outcomes in order.

    Outcomes are either a `requests.Response` to return, or an exception instance to raise.
    """

    def __init__(self, *outcomes):
        super().__init__()
        self.outcomes = list(outcomes)

    def send(self, request, **kwargs):
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        outcome.request = request
        outcome.url = request.url
        return outcome
