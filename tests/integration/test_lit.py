import re

from django.urls import reverse
from playwright.sync_api import Page, expect

from .common import PlaywrightTest


class TestLiterature(PlaywrightTest):
    def test_literature(self, live_server, page: Page):
        page.goto("/")

        # /lit/assessment/:id/
        self.login_and_goto_url(page, reverse("lit:overview", args=(2,)), "pm@hawcproject.org")
        assert page.locator("css=#tags .nestedTag").count() > 5

        # /lit/assessment/:id/references/
        page.locator("text=Browse").click()
        expect(page).to_have_url(reverse("lit:ref_list", args=(2,)))
        expect(page.locator("text=Human Study")).to_be_visible()
        expect(page.locator("#references_detail_div")).not_to_have_count(0)
        page.locator("text=Human Study").click()
        expect(page.locator(".referenceDetail")).to_have_count(2)

        # /lit/assessment/:id/references/visualization/
        page.goto(reverse("lit:ref_visual", args=(2,)))
        expect(page.locator("svg")).not_to_have_count(0)
        expect(page.locator("svg >> .tagnode")).to_have_count(4)

        # /lit/assessment/:id/references/search/
        page.goto(reverse("lit:ref_search", args=(2,)))
        page.locator("#ff-expand-form-toggle").click()
        page.locator("input[name=ref_search]").fill("Kawana")
        page.locator("text=Apply filters").click()
        expect(page.locator("text=References (1 found)")).to_be_visible()

        # /lit/assessment/:id/tag/
        page.goto(reverse("lit:tag", args=(1,)))
        expect(page.locator("text=Currently Applied Tags")).to_be_visible()

        # /lit/assessment/:id/tags/update/
        page.goto(reverse("lit:tags_update", args=(1,)))
        expect(page.locator("text=Reference tags for Chemical Z")).to_be_visible()

        # /lit/assessment/:id/tag/bulk/
        page.goto(reverse("lit:bulk_tag", args=(1,)))
        expect(
            page.locator("text=Select an Excel file (.xlsx) to load and process.")
        ).to_be_visible()

    def test_conflict_resolution(self, live_server, page: Page):
        page.goto("/")

        # /lit/assessment/:id/
        self.login_and_goto_url(
            page,
            reverse("lit:tag-conflicts", args=(4,)),
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
        page.goto(reverse("lit:ref_list", args=(4,)))
        page.locator("text=Animal Study").click()
        expect(
            page.locator(
                "text=Nutrient content of fish powder from low value fish and fish byproducts."
            )
        ).to_be_visible()
