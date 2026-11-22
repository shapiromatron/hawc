import pytest
from django.test import RequestFactory
from model_bakery import baker

from hawc.apps.common.auth import TokenBackend


def build_request(authorization: str | bytes | None = None):
    extra = {} if authorization is None else {"HTTP_AUTHORIZATION": authorization}
    return RequestFactory().get("/", **extra)


class TestTokenBackend:
    @pytest.mark.parametrize(
        ("authorization", "expected"),
        [
            ("Token abc", "abc"),
            ("token abc", "abc"),
            ("Bearer abc", ""),
            ("Token", ""),
            ("Token a b", ""),
            (b"Token \xff", ""),
            (None, ""),
        ],
    )
    def test_get_token_from_header(self, authorization, expected):
        request = build_request(authorization)
        assert TokenBackend().get_token_from_header(request) == expected

    def test_no_credentials(self):
        backend = TokenBackend()
        assert backend.authenticate(None) is None
        assert backend.authenticate(build_request()) is None

    def test_authenticate(self, db):
        user = baker.make("myuser.HAWCUser", is_active=True)
        baker.make("authtoken.Token", key="valid", user=user)
        backend = TokenBackend()
        assert backend.authenticate(None, token="valid") == user
        assert backend.authenticate(build_request("Token valid")) == user
        assert backend.authenticate(build_request("Token invalid")) is None

    def test_authenticate_inactive_user(self, db):
        user = baker.make("myuser.HAWCUser", is_active=False)
        baker.make("authtoken.Token", key="inactive", user=user)
        assert TokenBackend().authenticate(None, token="inactive") is None
