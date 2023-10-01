from playwright.sync_api import expect

from .common import PlaywrightTestCase


class TestCleanup(PlaywrightTestCase):
    def test_cleanup(self):
        page = self.page
        page.goto(self.live_server_url)

        # /assessment/:id/clean-extracted-data/
        self.login_and_goto_url(
            page, f"{self.live_server_url}/assessment/1/clean-extracted-data/", "pm@hawcproject.org"
        )
        expect(page.locator("text=Cleanup Chemical Z")).to_be_visible()

        page.locator("text=Endpoints").click()
        expect(page.locator("text=Cleanup Endpoints")).to_be_visible()
        page.locator("text=system").click()

        page.locator('textarea[name="system"]').fill("test")
        expect(page.locator("text=test (1)")).not_to_be_visible()
        page.locator("text=Submit bulk edit").click()
        expect(page.locator("text=test (1)")).to_be_visible()

        page.locator('textarea[name="system"]').fill("N/A")
        expect(page.locator("text=N/A (1)")).not_to_be_visible()
        page.locator("text=Submit bulk edit").click()
        expect(page.locator("text=N/A (1)")).to_be_visible()

        # /assessment/:id/clean-study-metrics/
        page.goto(f"{self.live_server_url}/assessment/1/clean-study-metrics/")
        expect(page.locator("text=Select the metric to edit")).to_be_visible()
        page.locator("text=Load responses").click()
        expect(page.locator('css=p:has-text("1 response met your criteria")')).to_be_visible()

        page.locator('input[name="checkbox-score-select"]').check()
        page.locator(".bulkEditForm >> select.form-control").select_option(
            "12"
        )  # Select Not reported
        page.locator("text=Bulk modify 1 item.").click()
        expect(page.locator('.score-bar:has-text("Not reported")')).to_be_visible()

        page.locator('input[name="checkbox-score-select"]').check()
        page.locator(".bulkEditForm >> select.form-control").select_option(
            "16"
        )  # Select Probably low risk of bias
        page.locator("text=Bulk modify 1 item.").click()
        expect(page.locator('.score-bar:has-text("Probably low risk of bias")')).to_be_visible()
