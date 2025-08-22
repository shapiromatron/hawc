import re

from playwright.sync_api import expect

from .common import PlaywrightTestCase


class TestBioassay(PlaywrightTestCase):
    def test_read(self):
        page = self.page
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

    def test_write(self):
        page = self.page
        page.goto(self.live_server_url)
        self.login_and_goto_url(page, f"{self.live_server_url}/study/1/", "team@hawcproject.org")
        page.locator("text=Actions").click()
        page.locator("text=Create new experiment").click()

        # create experiment
        expect(page).to_have_url(re.compile(r"/ani/study/\d+/experiment/create/"))
        page.locator('input[name="name"]').fill("test")
        page.locator('select[name="type"]').select_option("Sb")
        page.locator("text=Chemical purity available?").click()
        page.locator("#submit-id-save").click()

        # update experiment
        expect(page).to_have_url(re.compile(r"/ani/experiment/\d+/"))
        page.locator("text=Actions").click()
        page.locator("text=Update").first.click()

        expect(page).to_have_url(re.compile(r"/ani/experiment/\d+/update/"))
        page.locator('input[name="name"]').fill("test123")
        page.locator("text=Save").click()

        # create animal group
        expect(page).to_have_url(re.compile(r"/ani/experiment/\d+/"))
        page.locator("text=Actions").click()
        page.locator("text=Create new").click()

        expect(page).to_have_url(re.compile(r"/ani/experiment/\d+/animal-group/create/"))
        page.locator('input[name="name"]').fill("test123")
        page.locator('select[name="species"]').select_option("1")
        page.locator('select[name="sex"]').select_option("M")
        page.locator('select[name="route_of_exposure"]').select_option("OR")
        page.locator("#dose-unit-0").select_option("1")
        page.locator("#dose_0").fill("0")
        page.locator("#dose_1").fill("50")
        page.locator("#dose_2").fill("150")
        page.locator("#dose_3").fill("300")
        page.locator('input:has-text("Save")').click()

        # update animal group
        expect(page).to_have_url(re.compile(r"/ani/animal-group/\d+/"))
        page.locator("text=Actions").click()
        page.locator("text=Update").first.click()

        expect(page).to_have_url(re.compile(r"/ani/animal-group/\d+/update/"))
        page.locator('select[name="sex"]').select_option("F")
        page.locator("text=Save").click()

        # update dosing regime
        expect(page).to_have_url(re.compile(r"/ani/animal-group/\d+/"))
        page.locator("text=Actions").click()
        page.locator("text=Update").nth(2).click()

        expect(page).to_have_url(re.compile(r"/ani/dosing-regime/\d+/update/"))
        expect(page.locator("text=Add new representation")).to_be_visible()
        page.get_by_role("link", name="Add new representation").click()

        page.locator("#dose-unit-1").select_option("2")
        page.locator("#dose_0").nth(1).fill("0")
        page.locator("#dose_1").nth(1).fill("10")
        page.locator("#dose_2").nth(1).fill("20")
        page.locator("#dose_3").nth(1).fill("30")
        page.get_by_role("button", name="Save").click()

        expect(page).to_have_url(re.compile(r"/ani/animal-group/\d+/"))
        page.locator("text=Actions").click()
        page.locator("text=Create new").click()

        # create endpoint
        expect(page).to_have_url(re.compile(r"/ani/animal-group/\d+/endpoint/create/"))
        page.locator('[placeholder="Enter term ID"]').fill("5")
        page.locator("text=Load ID").click()
        page.locator('input[name="response_units"]').fill("mg")
        page.locator('input[name="form-0-n"]').fill("10")
        page.locator('input[name="form-1-n"]').fill("10")
        page.locator('input[name="form-2-n"]').fill("10")
        page.locator('input[name="form-3-n"]').fill("10")
        page.locator('input[name="form-0-response"]').fill("2.3")
        page.locator('input[name="form-1-response"]').fill("5.5")
        page.locator('input[name="form-2-response"]').fill("8.1")
        page.locator('input[name="form-3-response"]').fill("11.4")
        page.locator('input[name="form-0-variance"]').fill("2")
        page.locator('input[name="form-1-variance"]').fill("3")
        page.locator('input[name="form-2-variance"]').fill("4")
        page.locator('input[name="form-2-variance"]').fill("4")
        page.locator('input[name="form-3-variance"]').fill("5")
        page.locator('input[name="form-3-significance_level"]').fill("0.05")
        page.locator('select[name="form-2-treatment_effect"]').select_option("1")
        page.locator("text=Save").click()

        # update endpoint
        expect(page).to_have_url(re.compile(r"/ani/endpoint/\d+/"))
        page.locator("text=Actions").click()
        page.locator("text=Update endpoint").click()

        expect(page).to_have_url(re.compile(r"/ani/endpoint/\d+/update/"))
        page.locator('input[name="form-3-response"]').fill("17.4")
        page.locator("text=Save").click()

        # delete endpoint
        expect(page).to_have_url(re.compile(r"/ani/endpoint/\d+/"))
        page.locator("text=Actions").click()
        page.locator("text=Delete endpoint").click()

        expect(page).to_have_url(re.compile(r"/ani/endpoint/\d+/delete/"))
        page.locator("text=Delete endpoint").click()

        # delete animal-group
        expect(page).to_have_url(re.compile(r"/ani/animal-group/\d+/"))
        page.locator("text=Actions").click()
        page.locator('a:has-text("Delete")').click()

        expect(page).to_have_url(re.compile(r"/ani/animal-group/\d+/delete/"))
        page.locator("text=Delete animal-group").click()

        # delete experiment
        expect(page).to_have_url(re.compile(r"/ani/experiment/\d+/"))
        page.locator("text=Actions").click()
        page.locator('a:has-text("Delete")').click()

        expect(page).to_have_url(re.compile(r"/ani/experiment/\d+/delete/"))
        page.locator("text=Delete experiment").click()

        expect(page).to_have_url(re.compile(r"/study/\d+/"))
