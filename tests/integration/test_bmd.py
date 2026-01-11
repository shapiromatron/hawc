import re

from playwright.sync_api import expect

from .common import PlaywrightTestCase


class TestBmd(PlaywrightTestCase):
    def test_bmds2_view(self):
        # confirm that page renders
        page = self.page
        page.goto(self.live_server_url)

        self.login_and_goto_url(
            page, f"{self.live_server_url}/bmd/session/2/", "team@hawcproject.org"
        )
        page.get_by_role("tab", name="BMD setup").click()
        expect(page.get_by_role("heading", name="Selected models and options")).to_be_visible()

        page.get_by_role("tab", name="Results").click()
        expect(page.get_by_role("heading", name="BMDS output summary")).to_be_visible()

        page.get_by_role("tab", name="Model recommendation and").click()
        expect(page.get_by_role("columnheader", name="Recommendation")).to_be_visible()

    def test_dichotomous_execution(self):
        page = self.page
        page.goto(self.live_server_url)

        # go to bmd list for an endpoint
        self.login_and_goto_url(
            page, f"{self.live_server_url}/bmd/endpoint/12/", "team@hawcproject.org"
        )
        page.get_by_text("Actions").click()
        page.get_by_role("link", name="Create new").click()

        # execute an analysis
        page.get_by_role("button", name=re.compile("Execute Analysis")).click()
        expect(page.get_by_test_id("executing-spinner")).to_be_visible()  # todo - extend timeout?

        # click a modal
        page.get_by_role("button", name="Hill").click()
        expect(page.get_by_role("columnheader", name="Parameter Settings")).to_be_visible()
        page.get_by_label("Close").click()

        # select a model
        page.get_by_role("combobox").select_option("0")
        page.get_by_label("Selection notes").click()
        page.get_by_label("Selection notes").fill("selected")
        page.get_by_role("button", name="Save model selection").click()
        expect(page.get_by_test_id("select-model-confirmation")).to_be_visible()

    def test_continuous_execution(self):
        page = self.page
        page.goto(self.live_server_url)

        # go to bmd list for an endpoint
        self.login_and_goto_url(
            page, f"{self.live_server_url}/bmd/endpoint/13/", "team@hawcproject.org"
        )
        page.get_by_text("Actions").click()
        page.get_by_role("link", name="Create new").click()

        # execute an analysis
        page.get_by_role("button", name=re.compile("Execute Analysis")).click()
        expect(page.get_by_test_id("executing-spinner")).to_be_visible()  # todo - extend timeout?

        # click a modal
        page.get_by_role("button", name="Hill").click()
        expect(page.get_by_role("columnheader", name="Parameter Settings")).to_be_visible()
        page.get_by_label("Close").click()

        # select a model
        page.get_by_role("combobox").select_option("0")
        page.get_by_label("Selection notes").click()
        page.get_by_label("Selection notes").fill("selected")
        page.get_by_role("button", name="Save model selection").click()
        expect(page.get_by_test_id("select-model-confirmation")).to_be_visible()
