import re

from playwright.sync_api import expect

from .common import PlaywrightTestCase


class TestLiterature(PlaywrightTestCase):
    def test_literature(self):
        page = self.page
        page.goto(self.live_server_url)

        # /lit/assessment/:id/
        self.login_and_goto_url(
            page, f"{self.live_server_url}/lit/assessment/2/", "pm@hawcproject.org"
        )
        assert page.locator("css=#tags .nestedTag").count() > 5

        # /lit/assessment/:id/references/
        page.locator("text=Browse").click()
        expect(page).to_have_url(self.live_server_url + "/lit/assessment/2/references/")
        expect(page.locator("text=Human Study")).to_be_visible()
        expect(page.locator("#references_detail_div")).not_to_have_count(0)
        page.locator("text=Human Study").click()
        expect(page.locator(".referenceDetail")).to_have_count(2)

        # /lit/assessment/:id/references/visualization/
        page.goto(self.live_server_url + "/lit/assessment/2/references/visualization/")
        expect(page.locator("svg")).not_to_have_count(0)
        expect(page.locator("svg >> .tagnode")).to_have_count(4)

        # /lit/assessment/:id/references/search/
        page.goto(self.live_server_url + "/lit/assessment/2/references/search/")
        page.locator("#ff-expand-form-toggle").click()
        page.locator("input[name=ref_search]").fill("Kawana")
        page.locator("text=Apply filters").click()
        expect(page.locator("text=References (1 found)")).to_be_visible()

        # /lit/assessment/:id/tag/
        page.goto(self.live_server_url + "/lit/assessment/1/tag/")
        expect(page.locator("text=Currently Applied Tags")).to_be_visible()

        # /lit/assessment/:id/tags/update/
        page.goto(self.live_server_url + "/lit/assessment/1/tags/update/")
        expect(page.locator("text=Reference tags for Chemical Z")).to_be_visible()

        # /lit/assessment/:id/tag/bulk/
        page.goto(self.live_server_url + "/lit/assessment/1/tag/bulk/")
        expect(
            page.locator("text=Select an Excel file (.xlsx) to load and process.")
        ).to_be_visible()

    def test_conflict_resolution(self):
        page = self.page
        page.goto(self.live_server_url)

        # /lit/assessment/:id/
        self.login_and_goto_url(
            page,
            f"{self.live_server_url}/lit/assessment/4/reference-tag-conflicts/",
            "pm@hawcproject.org",
        )

        expect(
            page.locator(
                "text=Nutrient content of fish powder from low value fish and fish byproducts."
            )
        ).to_be_visible()
        expect(page.locator(".user-tag")).to_have_count(2)
        expect(page.locator(".conflict-reference-li")).to_have_count(1)

        with page.expect_response(re.compile(r"resolve_conflict")) as response_info:
            page.locator("text=Approve Team Member >> button").click()
            response = response_info.value
            assert response.ok

        # hides reference now that conflict is resolved
        expect(page.locator(".conflict-reference-li")).not_to_be_visible()

        # check that selected tag has been applied
        page.goto(f"{self.live_server_url}/lit/assessment/4/references/")
        page.locator("text=Animal Study").click()
        expect(
            page.locator(
                "text=Nutrient content of fish powder from low value fish and fish byproducts."
            )
        ).to_be_visible()

    def test_workflows(self):
        page = self.page
        page.goto(self.live_server_url)

        # /design/:id/
        self.login_and_goto_url(
            page, f"{self.live_server_url}/lit/assessment/4/workflows/", "pm@hawcproject.org"
        )

        expect(page.get_by_role("heading", name="Workflows")).to_be_visible()

        # Create workflow
        page.get_by_role("link", name="Create new workflow").click()
        page.get_by_label("Title*").click()
        page.get_by_label("Title*").fill("Title/Abstract")
        page.get_by_text("Link tagging").click()
        page.get_by_text("Link conflict resolution").click()
        page.get_by_role("group", name="Removal Criteria").get_by_label(
            "Tagged With:"
        ).select_option("32")
        page.locator("#div_id_removal_tags_descendants").get_by_text(
            "Include Descendants of above tag(s)"
        ).click()
        page.locator("#workflow-create").click()

        # Check workflow exists as expected
        expect(page.get_by_role("heading", name="Title/Abstract")).to_be_visible()
        expect(page.get_by_text("No admission criteria selected.")).to_be_visible()
        expect(
            page.get_by_text("Tagged with Inclusion (including descendant tags)")
        ).to_be_visible()
        expect(page.get_by_text("Conflict Resolution linked on Literature Review")).to_be_visible()
        expect(page.get_by_text("Tagging linked on Literature Review")).to_be_visible()

        # Update workflow
        page.get_by_title("Click to update").click()
        page.get_by_label("Title*").click()
        page.get_by_label("Title*").fill("Title/Abstract 2")
        page.locator("#workflow-update").click()

        # check update worked
        expect(page.get_by_role("heading", name="Title/Abstract 2")).to_be_visible()

        # Check that new Literature Review tiles have been added
        page.get_by_label("breadcrumb").get_by_role("link", name="Literature review").click()
        expect(page.get_by_text("in Title/Abstract 2")).to_be_visible()
        expect(page.get_by_role("link", name="1  needs tagging")).to_be_visible()
        expect(page.get_by_role("link", name=re.compile(r"\d+ ≠ with conflicts"))).to_be_visible()

        # go back and check delete
        page.get_by_text("Actions").click()
        page.get_by_role("link", name="View Workflows").click()
        page.get_by_title("Click to update").click()
        page.get_by_role("button", name=" Delete").click()
        expect(page.get_by_text("Are you sure you want to")).to_be_visible()
        page.get_by_role("button", name=" Delete").click()
        expect(page.get_by_role("heading", name="Title/Abstract 2")).not_to_be_visible()
