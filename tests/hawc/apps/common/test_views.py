import pytest
from django.test import RequestFactory
from django.urls import reverse

from hawc.apps.common.views import get_referrer


@pytest.mark.django_db
def test_get_referrer():
    factory = RequestFactory()

    request = factory.get("/")
    current_site = "testserver"
    default_url = f"https://{current_site}{reverse('portal')}"

    # url should resolve and will pass-through
    for good_url in [
        f"https://{current_site}{reverse('about')}",
        f"https://{current_site}{reverse('assessment:detail', args=(1,))}",
    ]:
        request = factory.get("/", HTTP_REFERER=good_url)
        assert get_referrer(request, default_url) == good_url

    # url doesn't resolve; should return default
    for bad_url in [
        "http://invalid-site.com",
        "https://invalid-site.com",
        "https://invalid-site.com:5555",
        f"http://{current_site}/bad-link-to-page/",
        f'http://{current_site}/onmouseover="alert(26)"',
        f"{default_url}?add-malicious-argument=1",
    ]:
        request = factory.get("/", HTTP_REFERER=bad_url)
        assert get_referrer(request, default_url) == default_url

    # extra arguments removed
    for bad_url in [
        f'https://{current_site}/portal/?onmouseover="alert(26)"&extra=true',
    ]:
        request = factory.get("/", HTTP_REFERER=bad_url)
        assert get_referrer(request, default_url) == f"https://{current_site}/portal/"

    # check default options
    request = factory.get("/")
    assert get_referrer(request, "/path-test/") == f"https://{current_site}/path-test/"
    assert (
        get_referrer(request, "https://complete-url.com/path-test/")
        == "https://complete-url.com/path-test/"
    )
