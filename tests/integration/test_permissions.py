from playwright.sync_api import expect

from .common import PlaywrightTestCase


class TestPermissions(PlaywrightTestCase):
    def test_permissions(self):
        """
        Basic permissions checks, ensure that some basic assessment-level checks are valid
        - unauthenticated users can view detail pages but not update pages
        - authenticated users with project permissions can view update pages
        """
        assessment_url = "/assessment/3/"
        detail_url = self.live_server_url + assessment_url
        edit_url = self.live_server_url + assessment_url + "update/"

        # check w/o authentication we can view the public url
        page = self.browser.new_page()
        page.goto(detail_url)
        expect(page.locator("h2 >> text=Chemical Y (2020)")).to_be_visible()

        # check we cannot go to edit url
        page.goto(edit_url)
        expect(page.locator("text=403. Forbidden")).to_be_visible()

        # login
        page.goto(self.live_server_url)
        self.login_and_goto_url(page, username="pm@hawcproject.org")
        expect(page).to_have_url(self.live_server_url + "/portal/")

        # now, try to go to edit url
        page.goto(edit_url)
        expect(page.locator("text=403. Forbidden")).not_to_be_visible()
