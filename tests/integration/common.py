import os

import pytest
from playwright.sync_api import Page

RUN_INTEGRATION = os.environ.get("INTEGRATION_TESTS") is not None
if RUN_INTEGRATION:
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


@pytest.mark.skipif(not RUN_INTEGRATION, reason="integration test")
class PlaywrightTest:
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
