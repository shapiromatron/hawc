from django.urls import reverse
from playwright.sync_api import Page, expect

from .common import PlaywrightTest


class TestMgmt(PlaywrightTest):
    def test_mgmt(self, live_server, page: Page):
        page.goto("/")

        # /mgmt/assessment/:id/
        self.login_and_goto_url(
            page, reverse("mgmt:task-dashboard", args=(1,)), "pm@hawcproject.org"
        )
        expect(page.locator("div.bar-all .js-plotly-plot")).to_have_count(1)
        expect(page.locator("div.bar-task .js-plotly-plot")).to_have_count(4)
        expect(page.locator("div.bar-user .js-plotly-plot")).to_have_count(1)

        # /mgmt/assessment/:id/details/
        page.goto(reverse("mgmt:task-list", args=(1,)))
        expect(page.locator(".task-row")).to_have_count(1)
