import pytest
from django.http import HttpRequest, HttpResponse
from django.test import TestCase
from django.test.client import Client, RequestFactory
from django.utils import timezone

from hawc.apps.common.middleware import (
    ActivateTimezoneMiddleware,
    CsrfRefererCheckMiddleware,
    MicrosoftOfficeLinkMiddleware,
)


class MicrosoftOfficeLinkMiddlewareTests(TestCase):
    def setUp(self):
        self.middleware = MicrosoftOfficeLinkMiddleware(lambda request: HttpResponse("passthrough"))
        self.request = HttpRequest()

    def test_office(self):
        """Ensure these strings do return custom middleware response"""
        agents = [
            # Office 2011 on Mac
            "Mozilla/5.0 (Macintosh; Intel Mac OS X) Word/14.20.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X) Excel/14.20.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X) PowerPoint/14.20.0",
            # Office on Windows 7
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; ms-office)",
        ]

        for agent in agents:
            self.request.META["HTTP_USER_AGENT"] = agent
            resp = self.middleware(self.request)
            assert isinstance(resp, HttpResponse)
            assert resp.getvalue().decode() == MicrosoftOfficeLinkMiddleware.RESPONSE_TEXT

    def test_not_matching(self):
        """Ensure Microsoft Outlook and other user-agents do exit early in middleware"""
        agents = [
            # Microsoft Outlook
            "Microsoft Office/14.0 (Windows NT 6.0; Microsoft Outlook 14.0.4760; Pro)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET4.0C; InfoPath.3; Microsoft Outlook 14.0.6131; ms-office; MSOffice 14)",
            # other common user-agents
            # https://techblog.willshouse.com/2012/01/03/most-common-user-agents/
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11) AppleWebKit/601.1.56 (KHTML, like Gecko) Version/9.0 Safari/601.1.56",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/601.1.56 (KHTML, like Gecko) Version/9.0 Safari/601.1.56",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:41.0) Gecko/20100101 Firefox/41.0",
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7",
        ]

        for agent in agents:
            self.request.META["HTTP_USER_AGENT"] = agent
            resp = self.middleware(self.request)
            assert isinstance(resp, HttpResponse)
            assert resp.getvalue().decode() == "passthrough"


class TestCsrfRefererCheckMiddleware:
    EXTERNAL_URL = "https://external-url.com"

    def test_passthrough(self):
        rf = RequestFactory()
        success = b"passthrough"
        middleware = CsrfRefererCheckMiddleware(lambda request: HttpResponse(success))

        # no header
        request = rf.get("/")
        resp = middleware(request)
        assert resp.getvalue() == success

        # valid referer/origin headers
        for key, value in [
            ("HTTP_REFERER", "http://testserver"),
            ("HTTP_ORIGIN", "http://testserver"),
        ]:
            request = rf.get("/")
            request.META[key] = value
            assert middleware(request).getvalue() == success

        # invalid refer/origin headers
        for key, value in [
            ("HTTP_REFERER", self.EXTERNAL_URL),
            ("HTTP_ORIGIN", self.EXTERNAL_URL),
        ]:
            request = rf.get("/")
            request.META[key] = value
            assert middleware(request).getvalue() == CsrfRefererCheckMiddleware.REFRESH

    @pytest.mark.django_db
    def test_integration(self):
        client = Client()

        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.content != CsrfRefererCheckMiddleware.REFRESH

        resp = client.get("/", HTTP_REFERER=self.EXTERNAL_URL)
        assert resp.content == CsrfRefererCheckMiddleware.REFRESH


class TestActivateTimezoneMiddleware:
    def _send_request(self, timezone: str | None):
        rf = RequestFactory()
        middleware = ActivateTimezoneMiddleware(lambda request: HttpResponse(b"ok"))
        request = rf.get("/")
        if timezone:
            request.COOKIES["timezone"] = timezone
        return middleware(request)

    def test_success(self):
        resp = self._send_request("Asia/Bangkok")
        assert resp.getvalue() == b"ok"
        assert timezone.get_current_timezone_name() == "Asia/Bangkok"
        timezone.deactivate()

    def test_invalid(self, settings):
        resp = self._send_request("Bad/Timezone")
        assert resp.getvalue() == b"ok"
        assert timezone.get_current_timezone_name() == settings.TIME_ZONE
        timezone.deactivate()

    def test_no_timezone(self, settings):
        resp = self._send_request(None)
        assert resp.getvalue() == b"ok"
        assert timezone.get_current_timezone_name() == settings.TIME_ZONE
        timezone.deactivate()
