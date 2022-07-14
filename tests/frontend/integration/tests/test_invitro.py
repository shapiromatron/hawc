import pytest
from playwright.sync_api import expect

from ..common import PlaywrightTestCase


@pytest.mark.django_db
class TestInvitro(PlaywrightTestCase):
    def test_invitro(self):
        page = self.browser.new_page()
        page.goto(self.live_server_url)

        # /in-vitro/assessment/:id/endpoint-categories/update/
        self.login_and_goto_url(
            page, f"{self.live_server_url}/in-vitro/assessment/2/endpoint-categories/update/", "pm@hawcproject.org"
        )
        expect(page.locator("text=Modify in-vitro endpoint categories")).to_be_visible()
