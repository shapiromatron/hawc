from django.urls import reverse
from playwright.sync_api import Page, expect

from .common import PlaywrightTest


class TestPermissions(PlaywrightTest):
    def test_permissions(self, live_server, page: Page):
        """
        Basic permissions checks, ensure that some basic assessment-level checks are valid
        - unauthenticated users can view detail pages but not update pages
        - authenticated users with project permissions can view update pages
        """
        detail_url = reverse("assessment:detail", args=(3,))
        edit_url = reverse("assessment:update", args=(3,))

        # check w/o authentication we can view the public url

        page.goto(detail_url)
        expect(page.locator("h2 >> text=Chemical Y (2020)")).to_be_visible()

        # check we cannot go to edit url
        page.goto(edit_url)
        expect(page.locator("text=403. Forbidden")).to_be_visible()

        # login
        page.goto("/")
        self.login_and_goto_url(page, username="pm@hawcproject.org")
        expect(page).to_have_url(reverse("portal"))

        # now, try to go to edit url
        page.goto(edit_url)
        expect(page.locator("text=403. Forbidden")).not_to_be_visible()
