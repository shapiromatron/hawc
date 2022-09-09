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
        page.locator("#design-update").click()
        page.locator('textarea[name="habitat_as_reported"]').click()
        page.locator('textarea[name="habitat_as_reported"]').fill("habitat update")
        page.locator("text=Save").click()

        # Create new Cause
        page.locator("#cause-create").click()
        page.locator('input[name="name"]').fill("new cause")
        page.locator('select[name="term"]+span.select2-container').click()
        page.locator('input[role="searchbox"]').type("term")
        page.locator('li[role="option"]:has-text("term")').click()
        page.locator('select[name="level"]+span.select2-container').click()
        page.locator('input[role="searchbox"]').fill("2")
        page.locator('select[name="level_units"]+span.select2-container').click()
        page.locator('input[role="searchbox"]').fill("grams")
        page.locator('select[name="duration"]+span.select2-container').click()
        page.locator('input[role="searchbox"]').fill("test")
        page.locator("#cause-save").click()
        # Copy cause
        page.locator("#cause-clone").nth(1).click()
        expect(page.locator("text=new cause (2)")).to_be_visible()
        # Delete new cause
        page.locator("#cause-delete").nth(2).click()
        page.locator("#cause-confirm-del").click()

        # Create effect
        page.locator("#effect-create").click()
        page.locator('input[name="name"]').fill("new effect")
        page.locator('select[name="term"]+span.select2-container').click()
        page.locator('input[role="searchbox"]').type("term")
        page.locator('li[role="option"]:has-text("term")').click()
        page.locator('select[name="units"]+span.select2-container').click()
        page.locator('input[role="searchbox"]').fill("grams")
        page.locator("#effect-save").click()
        # Copy effect
        page.locator("#effect-clone").nth(1).click()
        expect(page.locator("text=new effect (2)")).to_be_visible()
        # Delete copied effect
        page.locator("#effect-delete").nth(2).click()
        page.locator("#effect-confirm-del").click()

        # Create result
        page.locator("#result-create").click()
        page.locator('select[name="cause"]').select_option(index=2)
        page.locator('select[name="effect"]').select_option(index=2)
        page.locator('select[name="relationship_direction"]').select_option("0")
        page.locator('input[name="modifying_factors"]').click()
        page.locator('input[name="modifying_factors"]').fill("none")
        page.locator('select[name="variability"]').select_option("94")
        page.locator('select[name="statistical_sig_type"]').select_option("99")
        page.locator("#result-save").click()
        expect(page.locator('span:has-text("none")')).to_be_visible()
        # Copy result
        page.locator("#result-clone").nth(1).click()
        expect(page.locator('span:has-text("none")').nth(1)).to_be_visible()
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
