import os

import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from playwright.sync_api import Page

RUN_INTEGRATION = os.environ.get("HAWC_INTEGRATION_TESTS") is not None
if RUN_INTEGRATION:
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


@pytest.mark.skipif(not RUN_INTEGRATION, reason="integration test")
class PlaywrightTestCase(StaticLiveServerTestCase, TestCase):
    """
    We use a single class that inherits from both StaticLiveServerTestCase and TestCase
    in order to supersede properties of StaticLiveServerTestCase that cause the database to be
    flushed after every test, while still being able to utilize a live server for HTTP requests.

    Further reading: https://code.djangoproject.com/ticket/23640#comment:3
    """

    host = os.environ.get("LIVESERVER_HOST", "localhost")
    port = int(os.environ.get("LIVESERVER_PORT", 0))

    @pytest.fixture(autouse=True)
    def set_playwright(self, playwright, browser):
        self.playwright = playwright
        self.browser = browser

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
