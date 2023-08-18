from django.urls import reverse
from playwright.sync_api import Page, expect

from .common import PlaywrightTest


class TestEpi(PlaywrightTest):
    def test_epi(self, live_server, page: Page):
        page.goto("/")

        # /study-population/:id/
        self.login_and_goto_url(page, reverse("epi:sp_detail", args=(1,)), "pm@hawcproject.org")
        expect(page.locator("text=Case series")).to_be_visible()
        expect(page.locator("text=Study design")).to_be_visible()
        assert page.locator("li").count() > 3

        # /exposure/:id/
        page.goto(reverse("epi:exp_detail", args=(1,)))
        expect(page.locator("text=What was measured")).to_be_visible()
        expect(page.locator("tr >> text=What was measuredSarin")).to_be_visible()

        # /comparison-set/:id/
        page.goto(reverse("epi:cs_detail", args=(1,)))
        expect(page.locator("text=Exposure details")).to_be_visible()
        expect(page.locator("table")).not_to_have_count(0)
        expect(page.locator("#groups-table >> tbody >> tr")).to_have_count(3)

        # /outcome/:id/
        page.goto(reverse("epi:outcome_detail", args=(4,)))
        expect(page.locator("tr >> text=Namepartial PTSD")).to_be_visible()
        expect(page.locator(".nav.nav-tabs")).to_have_count(1)

        # /result/:id/
        page.goto(reverse("epi:result_detail", args=(1,)))
        expect(page.locator("text=Comparison set")).to_be_visible()
        expect(page.locator("#objContainer table")).to_have_count(2)
        expect(page.locator("text=Table 2")).to_be_visible()
        assert page.locator("tr").count() > 3
