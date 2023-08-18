from django.urls import reverse
from playwright.sync_api import Page, expect

from .common import PlaywrightTest


class TestInvitro(PlaywrightTest):
    def test_invitro(self, live_server, page: Page):
        page.goto("/")

        # /in-vitro/assessment/:id/endpoint-categories/update/
        self.login_and_goto_url(
            page,
            reverse("invitro:endpointcategory_update", args=(2,)),
            "pm@hawcproject.org",
        )
        expect(page.locator("text=Modify in-vitro endpoint categories")).to_be_visible()
