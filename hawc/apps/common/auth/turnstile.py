import pydantic
import requests
from crispy_forms import layout as cfl
from django import forms
from django.conf import settings


class SiteVerifyRequest(pydantic.BaseModel):
    secret: str
    response: str
    remoteip: str | None = None


class SiteVerifyResponse(pydantic.BaseModel):
    success: bool
    challenge_ts: str | None = None
    hostname: str | None = None
    error_codes: list[str] = pydantic.Field(alias="error-codes", default_factory=list)
    action: str | None = None
    cdata: str | None = None


def validate(turnstile_response: str, user_ip: str | None = None) -> SiteVerifyResponse:
    if not turnstile_response:
        return SiteVerifyResponse(success=False)
    url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    model = SiteVerifyRequest(
        secret=settings.TURNSTILE_KEY, response=turnstile_response, remoteip=user_ip
    )
    resp = requests.post(url, data=model.model_dump(), timeout=15)
    if resp.status_code != 200:
        model = SiteVerifyResponse(success=False, hostname=None)
        model.error_codes.extend(
            [f"Failure status code: {resp.status_code}", f"Failure details: {resp.text}"]
        )
        return model
    return SiteVerifyResponse(**resp.json())


class Turnstile:
    def __init__(self):
        self.enabled = len(settings.TURNSTILE_SITE) > 0

    def render(self):
        if not self.enabled:
            return None
        return cfl.HTML(
            f"""<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
        <div data-sitekey="{settings.TURNSTILE_SITE}" class="cf-turnstile"></div>
        """
        )

    def validate(self, data: dict):
        if self.enabled:
            value = data.get("cf-turnstile-response")
            response = validate(value)
            if not response.success:
                raise forms.ValidationError("Failed bot challenge - are you human?")
