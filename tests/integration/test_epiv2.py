import re

from playwright.sync_api import expect

from .common import PlaywrightTestCase


class TestEpiV2(PlaywrightTestCase):
    def test_epiv2(self):
        page = self.page
        page.goto(self.live_server_url)

        # /design/:id/
        self.login_and_goto_url(
            page, f"{self.live_server_url}/epidemiology/design/1/", "pm@hawcproject.org"
        )

        # Check that all tables are visible on detail page
        expect(page.locator("text=Chemicals")).to_be_visible()
        expect(page.locator("text=Exposure Measurements")).to_be_visible()
        expect(page.locator("text=Exposure Levels")).to_be_visible()
        expect(page.locator("text=Outcomes")).to_be_visible()
        expect(page.locator("text=Adjustment Factors")).to_be_visible()
        expect(page.locator("text=Data Extractions")).to_be_visible()

        # Go to update design page
        page.locator('a:has-text("Actions")').click()
        page.locator('a:has-text("Update")').click()

        # Update study design
        expect(page).to_have_url(re.compile(r"/epidemiology/design/\d+/update/"))
        expect(page.locator("text=Update design")).to_be_visible()
        page.locator("#design-update").click()
        page.locator('input[name="participant_n"]').fill("460")
        page.locator("text=Save").click()

        # Check chemical CCRUD
        page.locator("text=Chemicals Add Row >> button").click()
        page.locator('select[name="name"]+span.select2-container').click()
        page.locator('input[role="searchbox"]').fill("water")
        page.locator("#chemical-save").click()
        page.locator("text=water - >> #chemical-clone").click()
        page.locator("text=water (2)").click()
        page.locator("text=water (2) - >> #chemical-delete").click()
        page.locator("#chemical-confirm-del").click()

        # Check exposure CCRUD
        page.locator("text=Exposure Measurements Add Row >> button").click()
        page.locator('input[name="name"]').click()
        page.locator('input[name="name"]').fill("adult serum")
        page.locator('select[name="measurement_type_0"]').click()
        page.locator("#exposure-save").click()
        page.locator("text=adult serum Food - >> #exposure-clone").click()
        page.locator("text=adult serum (2)").click()
        page.locator("text=adult serum (2) Food - >> #exposure-delete").click()
        page.locator("#exposure-confirm-del").click()

        # Check exposure level CCRUD
        page.locator("text=Exposure Levels Add Row >> button").click()
        page.locator('input[name="name"]').click()
        page.locator('input[name="name"]').fill("water adult serum")
        page.locator('select[name="chemical"]').select_option("5")
        page.locator('select[name="exposure_measurement"]').select_option("4")
        page.locator("#exposurelevel-save").click()
        page.locator("text=water adult serum").click()
        page.locator("text=water adult serum water adult serum - - >> #exposurelevel-clone").click()
        page.locator("text=water adult serum (2)").click()
        page.locator(
            "text=water adult serum (2) water adult serum - - >> #exposurelevel-delete"
        ).click()
        page.locator("#exposurelevel-confirm-del").click()

        # Check outcome CCRUD
        page.locator("text=Outcomes Add Row >> button").click()
        page.locator('select[name="system"]').select_option("IM")
        page.locator('select[name="effect"]+span.select2-container').click()
        page.locator('input[role="searchbox"]').fill("asthma 2")
        page.locator('select[name="endpoint"]+span.select2-container').click()
        page.locator('input[role="searchbox"]').fill("asthma within previous 10 years")
        page.locator("#outcome-save").click()
        page.locator(
            "text=Immune asthma 2 asthma within previous 10 years >> #outcome-clone"
        ).click()
        page.locator(
            "text=Immune asthma 2 asthma within previous 10 years (2) >> #outcome-delete"
        ).click()
        page.locator("#outcome-confirm-del").click()

        # Check adjustment factor CCRUD
        page.locator("text=Adjustment Factors Add Row >> button").click()
        page.locator('input[name="name"]').click()
        page.locator('input[name="name"]').fill("B")
        page.locator('input[name="name"]').press("Tab")
        page.locator('textarea[name="description"]').fill("three, separate, items")
        page.locator("#adjustmentfactor-save").click()
        page.locator("text=three").click()
        page.locator("text=separate").click()
        page.locator("text=items").click()
        page.locator("text=B three separate items - >> #adjustmentfactor-clone").click()
        page.locator("text=B (2) three separate items - >> #adjustmentfactor-delete").click()
        page.locator("#adjustmentfactor-confirm-del").click()

        # Check data extraction CCRUD
        page.locator("text=Data Extractions Add Row >> button").click()
        page.locator('select[name="outcome"]').select_option("4")
        page.locator('select[name="exposure_level"]').select_option("7")
        page.locator('input[name="effect_estimate"]').click()
        page.locator('input[name="effect_estimate"]').fill("0")
        page.locator('input[name="group"]').click()
        page.locator('input[name="group"]').fill("Group 3")
        page.locator('select[name="factors"]').select_option("6")
        page.locator("#dataextraction-save").click()
        page.locator("text=Group 3").click()

        # Check that changes are reflected on detail page
        page.locator("#epiv2-page-cancel").click()
        expect(page.locator("text=460")).to_be_visible()
        expect(page.locator("text=water >> nth=0")).to_be_visible()
        expect(page.locator("text=adult serum >> nth=0")).to_be_visible()
        expect(page.locator("text=water adult serum >> nth=0")).to_be_visible()
        expect(page.locator("text=asthma within previous 10 years >> nth=0")).to_be_visible()
        expect(page.locator('td:has-text("B")').nth(4)).to_be_visible()
        expect(page.locator("text=Group 3")).to_be_visible()
