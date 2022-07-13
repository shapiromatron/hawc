import pytest
from playwright.sync_api import expect

from .common import PlaywrightTestCase


@pytest.mark.django_db
class TestStudy(PlaywrightTestCase):
    def test_study(self):
        page = self.browser.new_page()
        page.goto(self.live_server_url)

        # /study/assessment/:id/
        self.login_and_goto_url(
            page, f"{self.live_server_url}/study/assessment/2/", "pm@hawcproject.org"
        )
        expect(page.locator("text=Short citation")).to_be_visible()
        expect(page.locator("tbody tr")).to_have_count(4)

        # /study/:id/
        page.goto(self.live_server_url + "/study/7/")
        expect(page.locator("text=Animal bioassay")).to_be_visible()
        expect(page.locator("text=Biesemeier JA et al. 2011")).to_be_visible()

        expect(page.locator("#study_details")).not_to_have_count(0)
        expect(page.locator("table")).not_to_have_count(0)
        expect(page.locator("svg")).not_to_have_count(0)
        expect(page.locator("th >> text=Data type(s)")).to_have_count(4)
