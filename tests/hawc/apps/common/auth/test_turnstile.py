import json

import pytest
import requests
from django import forms

from hawc.apps.common.auth import turnstile


class PostRecorder:
    """A `requests.post` replacement which records calls and returns a configurable response."""

    def __init__(self, build_response):
        self.response = build_response(json.dumps({"success": True}))
        self.calls = []

    def __call__(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.response


@pytest.fixture
def post(build_response, monkeypatch):
    recorder = PostRecorder(build_response)
    monkeypatch.setattr(requests, "post", recorder)
    return recorder


class TestValidate:
    @pytest.mark.parametrize("value", ["", None])
    def test_no_response(self, post, value):
        result = turnstile.validate(value)
        assert result.success is False
        assert post.calls == []

    def test_success(self, build_response, post, settings):
        settings.TURNSTILE_KEY = "secret"
        post.response = build_response(
            json.dumps({"success": True, "hostname": "example.com", "error-codes": []})
        )
        result = turnstile.validate("token", user_ip="127.0.0.1")
        assert result.success is True
        assert result.hostname == "example.com"
        url, kwargs = post.calls[0]
        assert url == "https://challenges.cloudflare.com/turnstile/v0/siteverify"
        assert kwargs["data"] == {"secret": "secret", "response": "token", "remoteip": "127.0.0.1"}

    def test_challenge_failed(self, build_response, post):
        post.response = build_response(json.dumps({"success": False, "error-codes": ["bad"]}))
        result = turnstile.validate("token")
        assert (result.success, result.error_codes) == (False, ["bad"])

    def test_bad_status_code(self, build_response, post):
        post.response = build_response("oops", status_code=500)
        result = turnstile.validate("token")
        assert result.success is False
        assert result.error_codes == ["Failure status code: 500", "Failure details: oops"]


class TestTurnstile:
    def test_disabled(self, settings, post):
        settings.TURNSTILE_SITE = ""
        challenge = turnstile.Turnstile()
        assert challenge.enabled is False
        assert challenge.render() is None
        challenge.validate({})
        assert post.calls == []

    def test_render(self, settings):
        settings.TURNSTILE_SITE = "site-key"
        challenge = turnstile.Turnstile()
        assert challenge.enabled is True
        html = challenge.render().html
        assert 'data-sitekey="site-key"' in html
        assert "challenges.cloudflare.com/turnstile/v0/api.js" in html

    def test_validate(self, settings, post):
        settings.TURNSTILE_SITE = "site-key"
        turnstile.Turnstile().validate({"cf-turnstile-response": "token"})
        assert len(post.calls) == 1

    @pytest.mark.parametrize("data", [{}, {"cf-turnstile-response": "token"}])
    def test_validate_failure(self, build_response, settings, post, data):
        settings.TURNSTILE_SITE = "site-key"
        post.response = build_response(json.dumps({"success": False}))
        with pytest.raises(forms.ValidationError, match="Failed bot challenge"):
            turnstile.Turnstile().validate(data)
