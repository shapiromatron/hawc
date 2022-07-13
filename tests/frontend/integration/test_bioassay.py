import pytest
from playwright.sync_api import expect

from .common import PlaywrightTestCase


@pytest.mark.django_db
class TestBioassay(PlaywrightTestCase):
    def test_bioassay(self):
        page = self.browser.new_page()
        page.goto(self.live_server_url)

        # /experiment/:id/
        self.login_and_goto_url(
            page, f"{self.live_server_url}/ani/experiment/1/", "pm@hawcproject.org"
        )
        expect(page.locator("text=Multiple generations")).to_be_visible()
        expect(page.locator('css=#objContainer table:has-text("2 year bioassay")')).to_have_count(1)
        expect(page.locator("css=#ag-table tbody tr")).to_have_count(1)

        # /animal-group/:id/
        page.goto(f"{self.live_server_url}/ani/animal-group/1/")
        expect(page.locator("text=Dosing regime")).to_be_visible()
        expect(page.locator("text=sprague dawley")).to_be_visible()
        expect(page.locator("text=Oral diet")).to_be_visible()
        expect(page.locator("text=0, 10, 100 mg/kg/d")).to_be_visible()
        expect(page.locator("text=my outcome")).to_be_visible()

        # /endpoint/:id/
        page.goto(f"{self.live_server_url}/ani/endpoint/1/")
        expect(page.locator("text=my outcome")).not_to_have_count(0)
        expect(page.locator("css=svg")).not_to_have_count(0)
        expect(page.locator("css=.d3 .dr_dots .dose_points")).to_have_count(3)
        expect(page.locator("#dr-tbl")).not_to_have_count(0)
        expect(page.locator("#dr-tbl tr")).to_have_count(5)
