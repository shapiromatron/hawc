from playwright.sync_api import Page, expect

from .common import PlaywrightTest


class TestRoB(PlaywrightTest):
    def test_rob(self, live_server, page: Page):
        page.goto(live_server.url)

        # /rob/assessment/:id/
        self.login_and_goto_url(page, f"{live_server.url}/rob/assessment/1/", "pm@hawcproject.org")
        expect(page.locator("text=These are instructions")).to_be_visible()
        page.get_by_role("tab", name="Overview").click()
        expect(page.locator("text=Requirements by Study Type")).to_be_visible()

        # /rob/assessment/:id/study-assignments/
        page.goto(live_server.url + "/rob/assessment/1/study-assignments/")
        expect(page.locator("text=Foo et al.")).to_be_visible()
        assert page.locator("tr").count() >= 3
        assert page.locator("td").count() >= 4

        # /rob/assessment/1/study-assignments/update/
        page.goto(live_server.url + "/rob/assessment/1/study-assignments/update/")
        expect(page.locator("text=Individual reviews required:")).to_be_visible()
        assert page.locator("tr").count() >= 3
        assert page.locator("td").count() >= 4
        expect(page.locator("text=Foo et al.")).to_be_visible()
        expect(page.locator("text=Update")).not_to_have_count(0)
        expect(page.locator("text=Create")).not_to_have_count(0)

        # /rob/:id/update/
        page.goto(live_server.url + "/rob/3/update/")
        expect(page.locator(".score-form")).to_have_count(3)

        # /rob/study/:id/
        page.goto(live_server.url + "/rob/study/7/")
        expect(page.locator("text=Biesemeier JA et al. 2011: Risk of bias review")).to_be_visible()
        expect(page.locator(".aggregate-flex")).not_to_have_count(0)
        expect(page.locator(".aggregate-flex .domain-cell")).to_have_count(2)
