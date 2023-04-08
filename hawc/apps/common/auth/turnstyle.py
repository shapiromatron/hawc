import pydantic
import requests
from django.conf import settings


class SiteVerifyRequest(pydantic.BaseModel):
    secret: str
    response: str
    remoteip: str | None


class SiteVerifyResponse(pydantic.BaseModel):
    success: bool
    challenge_ts: str | None
    hostname: str | None
    error_codes: list[str] = pydantic.Field(alias="error-codes", default_factory=list)
    action: str | None
    cdata: str | None


def validate(turnstile_response: str, user_ip: str | None = None) -> SiteVerifyResponse:
    url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    model = SiteVerifyRequest(
        secret=settings.TURNSTYLE_KEY, response=turnstile_response, remoteip=user_ip
    )
    resp = requests.post(url, data=model.dict())
    if resp.status_code != 200:
        model = SiteVerifyResponse(success=False, hostname=None)
        model.error_codes.extend(
            [f"Failure status code: {resp.status_code}", f"Failure details: {resp.text}"]
        )
        return model
    return SiteVerifyResponse(**resp.json())
