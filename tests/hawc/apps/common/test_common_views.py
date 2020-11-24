from django.test import RequestFactory
from django.urls import reverse

from hawc.apps.common.views import get_referrer


def test_get_referrer():
    about_url = "https://example.com" + reverse("about")
    portal_url = "https://example.com" + reverse("portal")
    factory = RequestFactory()

    # url should resolve and will pass-through
    request = factory.get("/", HTTP_REFERER=about_url)
    assert get_referrer(request, portal_url) == about_url

    # url doesn't resolve; should return default
    request = factory.get("/", HTTP_REFERER=about_url + '"onmouseover="alert(26)"')
    assert get_referrer(request, portal_url) == portal_url
