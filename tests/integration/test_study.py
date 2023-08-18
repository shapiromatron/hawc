from playwright.sync_api import Page, expect

from .common import PlaywrightTest


class TestStudy(PlaywrightTest):
    def test_study(self, live_server, page: Page):
        page.goto(live_server.url)

        # /study/assessment/:id/
        self.login_and_goto_url(
            page, f"{live_server.url}/study/assessment/2/", "pm@hawcproject.org"
        )
        expect(page.locator("text=Short citation")).to_be_visible()
        expect(page.locator("tbody tr")).to_have_count(4)

        # /study/:id/
        page.goto(live_server.url + "/study/7/")
        expect(page.locator('td:has-text("Animal bioassay")')).to_be_visible()
        expect(page.locator('li:has-text("Biesemeier JA et al. 2011")')).to_be_visible()

        expect(page.locator("#study_details")).not_to_have_count(0)
        expect(page.locator("table")).not_to_have_count(0)
        expect(page.locator("svg")).not_to_have_count(0)
        expect(page.locator("th >> text=Data type(s)")).to_be_visible()
