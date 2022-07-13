import pytest
from playwright.sync_api import expect

from .common import PlaywrightTestCase


@pytest.mark.django_db
class TestEpi(PlaywrightTestCase):
    def test_epi(self):
        page = self.browser.new_page()
        page.goto(self.live_server_url)

        # /study-population/:id/
        self.login_and_goto_url(
            page, f"{self.live_server_url}/epi/study-population/1/", "pm@hawcproject.org"
        )
        expect(page.locator("text=Case series")).to_be_visible()
        expect(page.locator("text=Study design")).to_be_visible()
        assert page.locator("li").count() > 3

        # /exposure/:id/
        page.goto(f"{self.live_server_url}/epi/exposure/1/")
        expect(page.locator("text=What was measured")).to_be_visible()
        expect(page.locator("tr >> text=What was measuredSarin")).to_be_visible()

        # /comparison-set/:id/
        page.goto(f"{self.live_server_url}/epi/comparison-set/1/")
        expect(page.locator("text=Exposure details")).to_be_visible()
        expect(page.locator("table")).not_to_have_count(0)
        expect(page.locator("#groups-table >> tbody >> tr")).to_have_count(3)

        # /outcome/:id/
        page.goto(f"{self.live_server_url}/epi/outcome/4/")
        expect(page.locator("tr >> text=Namepartial PTSD")).to_be_visible()
        expect(page.locator(".nav.nav-tabs")).to_have_count(1)

        # /result/:id/
        page.goto(f"{self.live_server_url}/epi/result/1/")
        expect(page.locator("text=Comparison set")).to_be_visible()
        expect(page.locator("#objContainer table")).to_have_count(2)
        expect(page.locator("text=Table 2")).to_be_visible()
        assert page.locator("tr").count() > 3
