from playwright.sync_api import expect

from .common import PlaywrightTestCase


class TestMgmt(PlaywrightTestCase):
    def test_mgmt(self):
        page = self.page
        page.goto(self.live_server_url)

        # /mgmt/assessment/:id/
        self.login_and_goto_url(
            page, f"{self.live_server_url}/mgmt/assessment/1/", "pm@hawcproject.org"
        )
        expect(page.locator("div.bar-all .js-plotly-plot")).to_have_count(1)
        expect(page.locator("div.bar-task .js-plotly-plot")).to_have_count(4)
        expect(page.locator("div.bar-user .js-plotly-plot")).to_have_count(1)

        # /mgmt/assessment/:id/details/
        page.goto(self.live_server_url + "/mgmt/assessment/1/details/")
        expect(page.locator(".task-row")).to_have_count(4)
