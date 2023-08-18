import re

from django.urls import reverse
from playwright.sync_api import Page, expect

from .common import PlaywrightTest


class TestEpiV2(PlaywrightTest):
    def test_epiv2(self, live_server, page: Page):
        page.goto("/")

        # /design/:id/
        self.login_and_goto_url(
            page, reverse("epiv2:design_detail", args=(1,)), "pm@hawcproject.org"
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
        page.wait_for_load_state("networkidle")
        expect(page.locator("text=Update design")).to_be_visible()

        with page.expect_response(re.compile(r"/epidemiology/designv2/\d+/update/")) as resp:
            page.locator("#design-update").click()
        assert resp.value.ok is True

        page.locator('input[name="participant_n"]').fill("460")

        with page.expect_response(re.compile(r"/epidemiology/designv2/\d+/")) as resp:
            page.locator("text=Save").click()
        assert resp.value.ok is True

        # Chemical
        with page.expect_response(re.compile(r"/epidemiology/chemical/\d+/create/")) as resp:
            page.locator("text=Chemicals Add Row >> button").click()
        assert resp.value.ok is True

        page.locator('select[name="name"]+span.select2-container').click()
        page.locator('input[role="searchbox"]').fill("water")

        with page.expect_response(re.compile(r"/epidemiology/chemical/\d+/create/")) as resp:
            page.locator("#chemical-save").click()
        assert resp.value.ok is True

        with page.expect_response(re.compile(r"/epidemiology/chemical/\d+/clone/")) as resp:
            page.locator("#chemical-clone").nth(2).click()
        assert resp.value.ok is True

        page.locator("#chemical-delete").nth(3).click()
        with page.expect_response(re.compile(r"/epidemiology/chemical/\d+/delete/")) as resp:
            page.locator("#chemical-confirm-del").click()
        assert resp.value.ok is True

        # Exposure
        with page.expect_response(re.compile(r"/epidemiology/exposure/\d+/create/")) as resp:
            page.locator("text=Exposure Measurements Add Row >> button").click()
        assert resp.value.ok is True

        page.locator('input[name="name"]').fill("adult serum")
        page.locator('select[name="measurement_type_0"]').select_option(label="Food")

        with page.expect_response(re.compile(r"/epidemiology/exposure/\d+/create/")) as resp:
            page.locator("#exposure-save").click()
        assert resp.value.ok is True

        with page.expect_response(re.compile(r"/epidemiology/exposure/\d+/clone/")) as resp:
            page.locator("#exposure-clone").nth(1).click()
        assert resp.value.ok is True

        page.locator("#exposure-delete").nth(2).click()
        with page.expect_response(re.compile(r"/epidemiology/exposure/\d+/delete/")) as resp:
            page.locator("#exposure-confirm-del").click()
        assert resp.value.ok is True

        # Exposure level
        with page.expect_response(re.compile(r"/epidemiology/exposurelevel/\d+/create/")) as resp:
            page.locator("text=Exposure Levels Add Row >> button").click()
        assert resp.value.ok is True

        page.locator('input[name="name"]').click()
        page.locator('input[name="name"]').fill("water adult serum")
        page.locator('select[name="chemical"]').select_option(label="water")
        page.locator('select[name="exposure_measurement"]').select_option(label="adult serum")

        with page.expect_response(re.compile(r"/epidemiology/exposurelevel/\d+/create/")) as resp:
            page.locator("#exposurelevel-save").click()
        assert resp.value.ok is True

        with page.expect_response(re.compile(r"/epidemiology/exposurelevel/\d+/clone/")) as resp:
            page.locator("#exposurelevel-clone").nth(2).click()
        assert resp.value.ok is True

        page.locator("#exposurelevel-delete").nth(3).click()
        with page.expect_response(re.compile(r"/epidemiology/exposurelevel/\d+/delete/")) as resp:
            page.locator("#exposurelevel-confirm-del").click()
        assert resp.value.ok is True

        # Outcome
        with page.expect_response(re.compile(r"/epidemiology/outcome/\d+/create/")) as resp:
            page.locator("text=Outcomes Add Row >> button").click()
        assert resp.value.ok is True

        page.locator('select[name="system"]').select_option("IM")
        page.locator('select[name="effect"]+span.select2-container').click()
        page.locator('input[role="searchbox"]').fill("asthma 2")
        page.locator('select[name="endpoint"]+span.select2-container').click()
        page.locator('input[role="searchbox"]').fill("asthma within previous 10 years")

        # for some reason, issues using `click()`; fallback to keyboard operations
        btn = page.locator("#outcome-save")
        with page.expect_response(re.compile(r"/epidemiology/outcome/\d+/create/")) as resp:
            btn.focus()
            btn.press("Enter")
        assert resp.value.ok is True

        with page.expect_response(re.compile(r"/epidemiology/outcome/\d+/clone/")) as resp:
            page.locator("#outcome-clone").nth(1).click()
        assert resp.value.ok is True

        page.locator("#outcome-delete").nth(2).click()
        with page.expect_response(re.compile(r"/epidemiology/outcome/\d+/delete/")) as resp:
            page.locator("#outcome-confirm-del").click()
        assert resp.value.ok is True

        # Adjustment factor
        with page.expect_response(
            re.compile(r"/epidemiology/adjustmentfactor/\d+/create/")
        ) as resp:
            page.locator("text=Adjustment Factors Add Row >> button").click()
        assert resp.value.ok is True

        page.locator('input[name="name"]').fill("B")
        page.locator('textarea[name="description"]').fill("three, separate, items")

        with page.expect_response(
            re.compile(r"/epidemiology/adjustmentfactor/\d+/create/")
        ) as resp:
            page.locator("#adjustmentfactor-save").click()
        assert resp.value.ok is True

        with page.expect_response(re.compile(r"/epidemiology/adjustmentfactor/\d+/clone/")) as resp:
            page.locator("#adjustmentfactor-clone").nth(1).click()
        assert resp.value.ok is True

        page.locator("#adjustmentfactor-delete").nth(2).click()
        with page.expect_response(
            re.compile(r"/epidemiology/adjustmentfactor/\d+/delete/")
        ) as resp:
            page.locator("#adjustmentfactor-confirm-del").click()
        assert resp.value.ok is True

        # Data Extraction
        with page.expect_response(re.compile(r"/epidemiology/dataextraction/\d+/create/")) as resp:
            page.locator("text=Data Extractions Add Row >> button").click()
        page.locator('select[name="outcome"]').select_option(
            label="asthma within previous 10 years"
        )
        page.locator('select[name="exposure_level"]').select_option(label="water adult serum")
        page.locator('input[name="effect_estimate"]').fill("0")
        page.locator('input[name="group"]').fill("Group Z")
        page.locator('select[name="factors"]').select_option("6")

        with page.expect_response(re.compile(r"/epidemiology/dataextraction/\d+/create/")) as resp:
            page.locator("#dataextraction-save").click()
        assert resp.value.ok is True

        # Check that changes are reflected on detail page
        page.locator("#epiv2-page-cancel").click()
        expect(page).to_have_url(re.compile(r"/epidemiology/design/\d+/"))
        expect(page.locator("text=460")).to_be_visible()
        expect(page.locator("text=water >> nth=0")).to_be_visible()
        expect(page.locator("text=adult serum >> nth=0")).to_be_visible()
        expect(page.locator("text=water adult serum >> nth=0")).to_be_visible()
        expect(page.locator("text=asthma within previous 10 years >> nth=0")).to_be_visible()
        expect(page.locator('td:has-text("B")').nth(4)).to_be_visible()
        expect(page.locator("text=Group Z")).to_be_visible()
