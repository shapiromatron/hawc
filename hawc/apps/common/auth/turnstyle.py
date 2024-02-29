import pydantic
import requests
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
        secret=settings.TURNSTYLE_KEY, response=turnstile_response, remoteip=user_ip
    )
    resp = requests.post(url, data=model.model_dump())
    if resp.status_code != 200:
        model = SiteVerifyResponse(success=False, hostname=None)
        model.error_codes.extend(
            [f"Failure status code: {resp.status_code}", f"Failure details: {resp.text}"]
        )
        return model
    return SiteVerifyResponse(**resp.json())


class TurnstileWidget(forms.Widget):
    template_name = "common/widgets/turnstile.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        return data.get("cf-turnstile-response")

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs["data-sitekey"] = settings.TURNSTYLE_SITE
        return attrs

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["api_url"] = "https://challenges.cloudflare.com/turnstile/v0/api.js"
        return context


class TurnstileField(forms.Field):
    widget = TurnstileWidget

    def __init__(self, **kw):
        super().__init__(**kw)
        self.label = ""
        self.required = len(settings.TURNSTYLE_SITE) > 0

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs.update({"data-sitekey": settings.TURNSTYLE_SITE})
        return attrs

    def validate(self, value):
        super().validate(value)
        if self.required:
            response = validate(value)
            if not response.success:
                raise forms.ValidationError("Failed bot challenge - are you human?")
