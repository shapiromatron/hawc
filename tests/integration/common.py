import os

import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from playwright.sync_api import Page, sync_playwright

SKIP_INTEGRATION = os.environ.get("HAWC_INTEGRATION_TESTS") is None


@pytest.mark.skipif(SKIP_INTEGRATION, reason="integration test")
class PlaywrightTestCase(StaticLiveServerTestCase, TestCase):
    """
    We use a single class that inherits from both StaticLiveServerTestCase and TestCase
    in order to supersede properties of StaticLiveServerTestCase that cause the database to be
    flushed after every test, while still being able to utilize a live server for HTTP requests.

    Further reading: https://code.djangoproject.com/ticket/23640#comment:3
    """

    host = os.environ.get("LIVESERVER_HOST", "localhost")
    port = int(os.environ.get("LIVESERVER_PORT", 0))

    @classmethod
    def setUpClass(cls):
        # https://docs.djangoproject.com/en/3.2/topics/async/#async-safety
        # https://github.com/mxschmitt/python-django-playwright/blob/4d2235f4fadc66d88eed7b9cbc8d156c20575ad0/test_login.py
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.close()
        cls.playwright.stop()

    def login_and_goto_url(
        self, page: Page, url: str = "", username: str = "admin@hawcproject.org"
    ):
        """
        Login and go to the given url if one is given.

        Args:
            page (Page): login page
            url (str, optional): the URL to go to
            username (str, optional): User to login as; defaults to "admin@hawcproject.org"
        """

        page.locator('a.nav-link:has-text("Login")').click()
        page.locator('input[name="username"]').fill(username)
        page.locator('input[name="password"]').fill("pw")
        page.locator('input:has-text("Login")').click()
        if url:
            page.goto(url)
