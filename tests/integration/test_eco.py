import re

from playwright.sync_api import expect

from .common import PlaywrightTestCase


class TestEco(PlaywrightTestCase):
    def test_eco(self):
        page = self.page
        page.goto(self.live_server_url)

        # /study-population/:id/
        self.login_and_goto_url(page, f"{self.live_server_url}/eco/design/1/", "pm@hawcproject.org")

        # Check that all tables are visible on detail page
        expect(page.locator("text=Causes")).to_be_visible()
        expect(page.locator("text=Effects")).to_be_visible()
        expect(page.locator("text=Results")).to_be_visible()

        # Go to Update page
        page.locator("text=Actions").click()
        page.locator('a:has-text("Update")').click()

        # Update study design
        with page.expect_response(re.compile(r"/eco/designv2/\d+/update/")) as resp:
            page.locator("#design-update").click(delay=100)
        assert resp.value.ok is True
        page.locator('textarea[name="habitats_as_reported"]').click()
        page.locator('textarea[name="habitats_as_reported"]').fill("habitat update")
        page.locator("text=Save").click()

        # Create new Cause
        with page.expect_response(re.compile(r"/eco/cause/\d+/create/")) as resp:
            page.locator("#cause-create").click()
        assert resp.value.ok is True
        page.locator('input[name="name"]').fill("new cause")
        page.locator('select[name="term"]+span.select2-container').click()
        page.locator('input[role="searchbox"]').type("term")
        page.locator('li[role="option"]:has-text("term")').click()
        page.get_by_label("Level*").fill("test!")
        page.locator('select[name="duration"]+span.select2-container').click()
        page.locator('input[role="searchbox"]').fill("3 days")
        # buggy?
        page.locator("#cause-save").focus()
        page.locator("#cause-save").click(delay=100)
        page.locator("#cause-save").click(delay=100)
        # clone cause
        with page.expect_response(re.compile(r"/eco/cause/\d+/clone/")) as resp:
            page.locator("#cause-clone").nth(1).click(delay=100)
        assert resp.value.ok is True
        # Delete new cause
        page.locator("#cause-delete").nth(2).click()
        page.locator("#cause-confirm-del").click()

        # Create effect
        with page.expect_response(re.compile(r"/eco/effect/\d+/create/")) as resp:
            page.locator("#effect-create").click()
        assert resp.value.ok is True
        page.locator('input[name="name"]').fill("new effect")
        page.locator('select[name="term"]+span.select2-container').click()
        page.locator('input[role="searchbox"]').type("term")
        page.locator('li[role="option"]:has-text("term")').click()
        page.locator('select[name="units"]+span.select2-container').click()
        page.locator('input[role="searchbox"]').fill("grams")
        page.locator("#effect-save").click()
        # clone effect
        with page.expect_response(re.compile(r"/eco/effect/\d+/clone/")) as resp:
            page.locator("#effect-clone").nth(1).click(delay=100)
        assert resp.value.ok is True
        # Delete copied effect
        page.locator("#effect-delete").nth(2).click()
        page.locator("#effect-confirm-del").click()

        # Create result
        with page.expect_response(re.compile(r"/eco/result/\d+/create/")) as resp:
            page.locator("#result-create").click()
        assert resp.value.ok is True
        page.locator('input[name="name"]').fill("name!")
        page.locator('select[name="cause"]').select_option(index=2)
        page.locator('select[name="effect"]').select_option(index=2)
        page.locator('select[name="relationship_direction"]').select_option("0")
        page.locator('input[name="modifying_factors"]').click()
        page.locator('input[name="modifying_factors"]').fill("none")
        page.locator('select[name="variability"]').select_option("94")
        page.locator('select[name="statistical_sig_type"]').select_option("99")
        page.locator("#result-save").click()
        expect(page.locator('span:has-text("none")')).to_be_visible()
        # clone result
        with page.expect_response(re.compile(r"/eco/result/\d+/clone/")) as resp:
            page.locator("#result-clone").nth(1).click(delay=100)
        assert resp.value.ok is True
        # Delete copy
        page.locator("#result-delete").nth(2).click()
        page.locator("#result-confirm-del").click()

        # Expect page changes
        page.locator("#design-page-cancel").click()
        expect(page.locator("text=habitat update")).to_be_visible()
        expect(page.locator("text=new cause").nth(1)).to_be_visible()
        expect(page.locator("text=new effect").nth(1)).to_be_visible()
        expect(page.locator('span:has-text("none")')).to_be_visible()
        expect(page.locator("#result-tbody > tr")).to_have_count(2)
        expect(page.locator("#cause-tbody > tr")).to_have_count(2)
        expect(page.locator("#effect-tbody > tr")).to_have_count(2)
