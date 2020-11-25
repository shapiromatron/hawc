from urllib.parse import urlparse

import pytest
from django.test.client import Client
from django.urls import reverse

from hawc.apps.assessment.models import Assessment


class TestAssessmentClearCache:
    @pytest.mark.django_db
    def test_permissions(self, db_keys):
        url = Assessment.objects.get(id=db_keys.assessment_working).get_clear_cache_url()

        # test failures
        for client in ["reviewer@hawcproject.org", None]:
            c = Client()
            if client:
                assert c.login(username=client, password="pw") is True
            response = c.get(url)
            assert response.status_code == 403

        # test successes
        for client in ["pm@hawcproject.org", "team@hawcproject.org"]:
            c = Client()
            if client:
                assert c.login(username=client, password="pw") is True
            # this is success behavior in test environment w/o redis - TODO improve?
            with pytest.raises(NotImplementedError):
                response = c.get(url)

    @pytest.mark.django_db
    def test_functionality(self, db_keys):
        url = Assessment.objects.get(id=db_keys.assessment_working).get_clear_cache_url()
        c = Client()
        assert c.login(username="pm@hawcproject.org", password="pw") is True
        # this is success behavior in test environment w/o redis - TODO improve?
        with pytest.raises(NotImplementedError):
            c.get(url)


@pytest.mark.django_db
class TestAboutPage:
    def test_counts(self):
        client = Client()
        url = reverse("about")
        response = client.get(url)
        assert "counts" in response.context
        assert response.context["counts"]["assessments"] == 3
        assert response.context["counts"]["users"] == 5


def test_unsupported_browser():
    """
    Ensure our unsupported browser warning will appear with some user agents
    """
    WARNING = "Your current browser has not been tested extensively"

    uas = [
        ("ie11", False),
        ("firefox", True),
    ]

    for ua, valid in uas:
        c = Client(HTTP_USER_AGENT=ua)
        response = c.get("/")
        assert response.context["UA_SUPPORTED"] is valid
        assert (WARNING in response.content.decode("utf8")) is (not valid)


@pytest.mark.django_db
class TestContactUsPage:
    def test_login_required(self):
        contact_url = reverse("contact")

        client = Client()

        # login required
        resp = client.get(contact_url)
        assert resp.status_code == 302
        assert urlparse(resp.url).path == reverse("user:login")

        # valid
        client.login(username="pm@hawcproject.org", password="pw")
        resp = client.get(contact_url)
        assert resp.status_code == 200

    def test_referrer(self):
        portal_url = reverse("portal")
        about_url = reverse("about")
        contact_url = reverse("contact")

        client = Client()
        client.login(username="pm@hawcproject.org", password="pw")

        # no referrer; use default
        resp = client.get(contact_url)
        assert resp.context["form"].fields["previous_page"].initial == portal_url

        # valid referrer; use valid
        resp = client.get(contact_url, HTTP_REFERER=about_url)
        assert resp.context["form"].fields["previous_page"].initial == about_url

        # invalid referrer; use default
        about_url = reverse("about")
        resp = client.get(contact_url, HTTP_REFERER=about_url + '"onmouseover="alert(26)"')
        assert resp.context["form"].fields["previous_page"].initial == portal_url
