from playwright.sync_api import expect

from .common import PlaywrightTestCase


class TestLiterature(PlaywrightTestCase):
    def test_literature(self):
        page = self.page
        page.goto(self.live_server_url)

        # /lit/assessment/:id/
        self.login_and_goto_url(
            page, f"{self.live_server_url}/lit/assessment/2/", "pm@hawcproject.org"
        )
        assert page.locator("css=#tags .nestedTag").count() > 5

        # /lit/assessment/:id/references/
        page.locator("text=Browse").click()
        expect(page).to_have_url(self.live_server_url + "/lit/assessment/2/references/")
        expect(page.locator("text=Human Study (2)")).to_be_visible()
        expect(page.locator("#references_detail_div")).not_to_have_count(0)
        page.locator("text=Human Study (2)").click()
        expect(page.locator(".referenceDetail")).to_have_count(2)

        # /lit/assessment/:id/references/visualization/
        page.goto(self.live_server_url + "/lit/assessment/2/references/visualization/")
        expect(page.locator("svg")).not_to_have_count(0)
        expect(page.locator("svg >> .tagnode")).to_have_count(4)

        # /lit/assessment/:id/references/search/
        page.goto(self.live_server_url + "/lit/assessment/2/references/search/")
        page.locator("text=Filter references").click()
        page.locator("input[name=authors]").fill("Kawana")
        page.locator("text=Apply filters").click()
        expect(page.locator("text=References (1 found)")).to_be_visible()

        # /lit/assessment/:id/tag/untagged/
        page.goto(self.live_server_url + "/lit/assessment/1/tag/untagged/")
        expect(page.locator("text=Currently Applied Tags")).to_be_visible()

        # /lit/assessment/:id/tags/update/
        page.goto(self.live_server_url + "/lit/assessment/1/tags/update/")
        expect(page.locator("text=Reference tags for Chemical Z")).to_be_visible()

        # /lit/assessment/:id/tag/bulk/
        page.goto(self.live_server_url + "/lit/assessment/1/tag/bulk/")
        expect(
            page.locator("text=Select an Excel file (.xlsx) to load and process.")
        ).to_be_visible()
