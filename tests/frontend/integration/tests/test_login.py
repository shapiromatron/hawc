import re

import pytest
from playwright.sync_api import expect

from ..common import PlaywrightTestCase


@pytest.mark.django_db
class TestLogin(PlaywrightTestCase):
    def test_login(self):
        """
        expect( that we're able to login/logout successfully and an errors are displayed as expected.
        """
        page = self.browser.new_page()
        page.goto(self.live_server_url)

        expect(page.locator("a >> text=Login")).to_be_visible()
        page.locator("a >> text=Login").click()
        expect(page).to_have_url(re.compile(r"/user/login/"))

        # invalid password check
        msg = "Please enter a correct email and password."
        expect(page.locator(f"text={msg}")).not_to_be_visible()
        page.locator('input[name="username"]').fill("admin@hawcproject.org")
        page.locator('input[name="password"]').fill("not my password")

        page.locator('input:has-text("Login")').click()
        expect(page.locator(f"text={msg}")).to_be_visible()
        expect(page).to_have_url(re.compile(r"/user/login/"))

        # confirm correct login
        page.locator('input[name="username"]').fill("admin@hawcproject.org")
        page.locator('input[name="password"]').fill("pw")
        page.locator('input:has-text("Login")').click()
        expect(page).to_have_url(self.live_server_url + "/portal/")

        # confirm logout
        page.locator("#navbarDropdownMenuLink").click()
        page.locator("div.dropdown-menu >> text=Logout").click()
        expect(page).to_have_url(self.live_server_url + "/")
