import pytest
from playwright.sync_api import expect

from .common import PlaywrightTestCase


@pytest.mark.django_db
class TestMgmt(PlaywrightTestCase):
    def test_mgmt(self):
        page = self.browser.new_page()
        page.goto(self.live_server_url)

        # /mgmt/assessment/:id/
        self.login_and_goto_url(
            page, f"{self.live_server_url}/mgmt/assessment/1/", "pm@hawcproject.org"
        )
        expect(page.locator("div.barAll")).to_have_count(1)
        expect(page.locator("div.barTask")).to_have_count(4)
        expect(page.locator("div.barUser")).to_have_count(1)

        # /mgmt/assessment/:id/details/
        page.goto(self.live_server_url + "/mgmt/assessment/1/details/")
        expect(page.locator(".taskStudyRow")).to_have_count(1)
