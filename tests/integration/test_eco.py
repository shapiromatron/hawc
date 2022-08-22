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
        page.locator('input[name="term_0"]').click()
        page.locator('input[name="term_0"]').fill("term")
        page.locator('span:has-text("term")').click()
        page.locator('input[name="level"]').click()
        page.locator('input[name="level"]').fill("2")
        page.locator('input[name="level_units"]').click()
        page.locator('input[name="level_units"]').fill("g")
        page.locator('input[name="duration"]').click()
        page.locator('input[name="duration"]').fill("2")
        page.locator('input[name="name"]').fill("new cause")
        page.locator("#div_id_as_reported > div > .ql-container > .ql-editor").click()
        page.keyboard.type("cause as reported")
        page.locator("#cause-save").click()
        # Copy cause
        page.locator("#cause-2 >> #cause-clone").click()
        expect(page.locator("text=new cause (2)")).to_be_visible()
        # Delete new cause
        page.locator("#cause-3 >> #cause-delete").click()
        page.locator("#cause-confirm-del").click()
        # Create effect
        page.locator("#effect-create").click()
        page.locator('input[name="name"]').click()
        page.locator('input[name="name"]').fill("new effect")
        page.locator('input[name="term_0"]').click()
        page.locator('input[name="term_0"]').fill("term")
        page.locator("#ui-id-4").click()
        page.locator('input[name="units"]').click()
        page.locator('input[name="units"]').fill("g")
        page.locator("#div_id_as_reported > div > .ql-container > .ql-editor").click()
        page.keyboard.type("effect as reported")
        page.locator("#effect-save").click()
        # Copy effect
        page.locator("#effect-2 >> #effect-clone").click()
        expect(page.locator("text=new effect (2)")).to_be_visible()
        # Delete copied effect
        page.locator("#effect-3 >> #effect-delete").click()
        page.locator("#effect-confirm-del").click()
        # Create result
        page.locator("#result-create").click()
        page.locator('select[name="cause"]').select_option("2")
        page.locator('select[name="effect"]').select_option("2")
        page.locator('input[name="sort_order"]').click()
        page.locator('select[name="relationship_direction"]').select_option("0")
        page.locator('input[name="modifying_factors"]').click()
        page.locator('input[name="modifying_factors"]').fill("none")
        page.locator('select[name="variability"]').select_option("94")
        page.locator('select[name="statistical_sig_type"]').select_option("99")
        page.locator("#result-save").click()
        expect(page.locator('span:has-text("none")')).to_be_visible()
        # Copy result
        page.locator("#result-2 >> #result-clone").click()
        expect(page.locator("#result-3")).to_be_visible()
        # Delete copy
        page.locator("#result-3 >> #result-delete").click()
        page.locator("text=Confirm").click()
        page.locator("#design-page-cancel").click()

        # Expect page changes
        expect(page.locator("text=habitat update")).to_be_visible()
        expect(page.locator("text=new cause").nth(1)).to_be_visible()
        expect(page.locator("text=new effect").nth(1)).to_be_visible()
        expect(page.locator('span:has-text("none")')).to_be_visible()
