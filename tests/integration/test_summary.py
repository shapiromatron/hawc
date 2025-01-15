import re

from playwright.sync_api import expect

from .common import PlaywrightTestCase


class TestSummary(PlaywrightTestCase):
    def test_exploratory_heatmaps(self):
        """
        Assert we have a list of built-in exploratory heatmap tables and they render.
        """
        page = self.page
        page.goto(self.live_server_url)

        # /assessment/:id/endpoints/
        self.login_and_goto_url(
            page, f"{self.live_server_url}/assessment/2/endpoints/", "pm@hawcproject.org"
        )
        expect(page.locator("tr")).to_have_count(3)
        expect(page.locator("td")).to_have_count(8)
        expect(page.locator('tr >> nth=0:has-text("Bioassay")'))
        expect(page.locator('tr >> nth=1:has-text("Epidemiology")'))

        # /ani/assessment/:id/heatmap-study-design/
        page.goto(self.live_server_url + "/ani/assessment/2/heatmap-study-design/")
        expect(page.locator("svg")).not_to_have_count(0)
        expect(page.locator(".exp_heatmap_cell")).to_have_count(6)

    def test_browsing(self):
        """
        Assert we can render the completed HAWC visualizations. This includes:

        - the visuals list page
        - a data pivot summary page
        - a risk of bias heatmap can be rendered
        """
        page = self.page
        page.goto(self.live_server_url)

        # /summary/assessment/2/visuals/
        self.login_and_goto_url(
            page, f"{self.live_server_url}/summary/assessment/2/visuals/", "pm@hawcproject.org"
        )
        expect(page.locator("text=Available visualizations")).to_be_visible()
        assert page.locator("tr").count() > 10

        # data pivot
        page.locator("text='data pivot - animal bioassay - endpoint'").click()
        expect(page).to_have_url(re.compile(r"animal-bioassay-data-pivot-endpoint"))
        expect(page.locator('.dropdown-toggle:has-text("Actions")')).to_be_visible()
        expect(page.locator("text=study name")).not_to_have_count(0)
        assert page.locator("#dp_display svg g g path").count() > 7
        page.locator('button[title="Download figure"] >> nth=0').click()
        expect(page.locator("text=Download as a SVG")).to_be_visible()

        # rob heatmap
        page.goto(self.live_server_url + "/summary/assessment/2/visuals/")
        page.locator("text='rob-heatmap'").click()
        expect(page).to_have_url(re.compile(r"rob-heatmap"))
        expect(page.locator('.dropdown-toggle:has-text("Actions")')).not_to_be_visible()
        expect(page.locator("svg.d3")).not_to_have_count(0)
        assert page.locator("svg.d3 g rect").count() > 5

    def test_visuals(self):
        """
        Tests to ensure all visual types are displayed.
        """
        page = self.page
        page.goto(self.live_server_url)

        # visual id should redirect to slug url
        self.login_and_goto_url(
            page, f"{self.live_server_url}/summary/visual/5/", "pm@hawcproject.org"
        )
        expect(page).to_have_url(re.compile(r"/summary/visual/assessment/2/rob-barchart/"))
        expect(page.locator("svg.d3")).to_be_visible()
        expect(page.locator("svg >> .legend")).not_to_have_count(0)

        page.goto(self.live_server_url + "/summary/visual/assessment/2/crossview/")
        expect(page.locator("text=dose")).not_to_have_count(0)
        expect(page.locator("svg.d3")).to_be_visible()
        expect(page.locator("svg >> .crossview_path_group")).not_to_have_count(0)

        page.goto(
            self.live_server_url
            + "/summary/data-pivot/assessment/2/animal-bioassay-data-pivot-endpoint/"
        )
        expect(page.locator("svg.d3")).to_be_visible()
        expect(page.locator("svg >> .x_gridlines")).not_to_have_count(0)
        expect(page.locator("svg >> .y_gridlines")).not_to_have_count(0)

        page.goto(self.live_server_url + "/summary/data-pivot/assessment/2/data-pivot-epi/")
        expect(page.locator("svg.d3")).to_be_visible()
        expect(page.locator("svg >> .x_gridlines")).not_to_have_count(0)
        expect(page.locator("svg >> .y_gridlines")).not_to_have_count(0)

        page.goto(self.live_server_url + "/summary/visual/assessment/2/embedded-tableau/")
        expect(page.locator("h2:has-text('embedded-tableau')")).to_be_visible()
        expect(page.locator("tableau-viz >> iframe")).to_be_visible()
        expect(page.locator("iframe")).not_to_have_count(0)

        page.goto(self.live_server_url + "/summary/visual/assessment/2/rob-heatmap/")
        expect(page.locator("h2:has-text('rob-heatmap')")).to_be_visible()
        expect(page.locator("svg.d3")).to_be_visible()
        expect(page.locator("svg >> .legend")).not_to_have_count(0)

        page.goto(self.live_server_url + "/summary/visual/assessment/2/tagtree/")
        expect(page.locator("text='Human Study'")).to_be_visible()
        expect(page.locator("svg.d3")).to_be_visible()
        expect(page.locator("svg >> .tagnode")).to_have_count(5)

        page.goto(self.live_server_url + "/summary/visual/assessment/2/exploratory-heatmap/")
        expect(page.locator("h2:has-text('exploratory-heatmap')")).to_be_visible()
        expect(page.locator("svg.d3")).to_be_visible()
        assert page.locator("svg.d3 >> g >> rect").count() > 5

        page.goto(self.live_server_url + "/summary/visual/assessment/2/bioassay-aggregation/")
        expect(page.locator("h2:has-text('bioassay-aggregation')")).to_be_visible()
        expect(page.locator("svg.d3")).to_be_visible()
        assert page.locator("svg.d3 >> g >> circle").count() > 5

        page.goto(self.live_server_url + "/summary/visual/assessment/2/plotly/")
        expect(page.locator("h2:has-text('plotly')")).to_be_visible()
        expect(page.locator(".plotly")).to_be_visible()

        page.goto(self.live_server_url + "/summary/visual/assessment/2/image/")
        expect(page.locator("h2:has-text('image')")).to_be_visible()
        expect(page.locator("#visual-image").get_by_role("img")).to_be_visible()

        page.goto(self.live_server_url + "/summary/visual/assessment/2/prisma-visual/")
        expect(page.locator("h2:has-text('prisma visual')")).to_be_visible()
        expect(page.locator("svg.d3")).to_be_visible()
        assert page.locator("svg.d3 >> g >> rect").count() == 6

    def test_tables(self):
        """
        Tests to ensure all visual types are displayed.
        """
        page = self.page
        page.goto(self.live_server_url)

        # check summary table
        self.login_and_goto_url(
            page, self.live_server_url + "/summary/assessment/1/tables/", "pm@hawcproject.org"
        )
        expect(page.locator("text=Available tables")).to_be_visible()
        expect(page.locator("table >> tbody >> tr")).to_have_count(3)

        # check generic table
        page.goto(self.live_server_url + "/summary/assessment/1/tables/Generic-1/")
        expect(page.locator(".summaryTable")).to_be_visible()

        # check evidence profile
        page.goto(self.live_server_url + "/summary/assessment/1/tables/Evidence-Profile-1/")
        expect(page.locator(".summaryTable")).to_be_visible()

        # check study evaluation
        page.goto(self.live_server_url + "/summary/assessment/1/tables/Study-Evaluation-1/")
        expect(page.locator(".summaryTable")).to_be_visible()

    def test_modals(self):
        """
        Tests to ensure that modals on visuals are working correctly.
        """
        page = self.page
        page.goto(self.live_server_url)

        # check study display modal
        self.login_and_goto_url(
            page,
            self.live_server_url
            + "/summary/data-pivot/assessment/2/animal-bioassay-data-pivot-endpoint/",
            "pm@hawcproject.org",
        )
        expect(page.locator("text=study name")).to_be_visible()
        page.locator("text='Biesemeier JA et al. 2011' >> nth=0").click()
        expect(page.locator("text='Click on any cell above to view details.'")).to_be_visible()
        page.locator("text='Show all details'").click()
        expect(page.locator("text='metric 1'")).to_be_visible()
        expect(page.locator("h3 >> text='overall'")).to_be_visible()
        page.locator("text='Hide all details'").click()
        expect(page.locator("text=metric 1")).not_to_be_visible()
        expect(page.locator("h3 >> text='overall'")).not_to_be_visible()
        page.locator("text='domain 1'").click()
        expect(page.locator("text='metric 1'")).to_be_visible()
        expect(page.locator("text='overall metric 1'")).not_to_be_visible()
        page.locator("text='overall'").click()
        expect(page.locator("text='metric 1'")).not_to_be_visible()
        expect(page.locator("text='overall metric 1'")).to_be_visible()
        page.locator("button:has-text('Close')").click()
        expect(page.locator("text='Click on any cell above to view details.'")).not_to_be_visible()
