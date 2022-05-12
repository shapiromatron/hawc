import helium

from . import shared


def _check_exploratory_heatmaps(driver, root_url):
    """
    Assert we have a list of built-in exploratory heatmap tables and they render.
    """
    # /assessment/:id/endpoints/
    helium.go_to(root_url + "/assessment/2/endpoints/")
    assert len(driver.find_elements_by_css_selector("tr")) == 3
    assert len(driver.find_elements_by_css_selector("td")) == 8
    assert helium.Text(below="Data type").value == "Bioassay"
    assert helium.Text(below="Bioassay").value == "Epidemiology"

    # /ani/assessment/:id/heatmap-study-design/
    helium.go_to(root_url + "/ani/assessment/2/heatmap-study-design/")
    helium.wait_until(condition_fn=helium.Text("Grand Total").exists, timeout_secs=60)
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector(".exp_heatmap_cell")) == 6


def _check_browsing(driver, root_url):
    """
    Assert we can render the completed HAWC visualizations. This includes:

    - the visuals list page
    - a data pivot summary page
    - a risk of bias heatmap can be rendered
    """

    # go to website
    helium.go_to(root_url + "/summary/assessment/2/visuals/")
    assert helium.Text("Available visualizations").exists() is True
    helium.wait_until(helium.Text("Title").exists)
    assert len(driver.find_elements_by_css_selector("tr")) > 10

    # view data pivot
    helium.scroll_down(600)
    helium.click("data pivot - animal bioassay - endpoint")
    assert "animal-bioassay-data-pivot-endpoint" in driver.current_url
    assert helium.Link("Actions").exists() is True
    helium.wait_until(helium.Text("study name").exists)
    assert len(driver.find_elements_by_css_selector("#dp_display svg")) > 0
    assert len(driver.find_elements_by_css_selector("#dp_display svg g g path")) > 7
    driver.find_elements_by_css_selector('button[title="Download figure"]')[0].click()
    assert helium.Text("Download as a SVG").exists() is True

    # view browse again
    helium.go_to(root_url + "/summary/assessment/2/visuals/")
    helium.wait_until(helium.Text("Title").exists)

    # click the rob heatmap example
    driver.find_element_by_link_text("rob-heatmap").click()
    assert "rob-heatmap" in driver.current_url
    helium.wait_until(helium.Text("rob-heatmap").exists)
    assert helium.Link("Actions").exists() is False
    assert len(driver.find_elements_by_css_selector("svg.d3")) > 0
    assert len(driver.find_elements_by_css_selector("svg.d3 g rect")) > 5


def _check_visuals_working(driver, root_url):
    """
    Tests to ensure all visual types are displayed.
    """
    helium.go_to(root_url + "/summary/visual/5/")
    # visual id should redirect to slug url
    helium.wait_until(lambda: "/summary/visual/assessment/2/barchart/" in driver.current_url)
    helium.wait_until(helium.Text("legend").exists)
    helium.wait_until(helium.S("svg.d3").exists)
    assert len(driver.find_elements_by_css_selector("svg .legend")) > 0

    helium.go_to(root_url + "/summary/visual/assessment/2/crossview/")
    helium.wait_until(helium.Text("Dose").exists)
    helium.wait_until(helium.S("svg.d3").exists)
    assert len(driver.find_elements_by_css_selector("svg .crossview_path_group")) > 0

    helium.go_to(root_url + "/summary/data-pivot/assessment/2/animal-bioassay-data-pivot-endpoint/")
    helium.wait_until(helium.Text("study name").exists)
    helium.wait_until(helium.S("svg.d3").exists)
    assert len(driver.find_elements_by_css_selector("svg .x_gridlines")) > 0
    assert len(driver.find_elements_by_css_selector("svg .y_gridlines")) > 0

    helium.go_to(root_url + "/summary/data-pivot/assessment/2/data-pivot-epi/")
    helium.wait_until(helium.Text("study name").exists)
    helium.wait_until(helium.S("svg.d3").exists)
    assert len(driver.find_elements_by_css_selector("svg .x_gridlines")) > 0
    assert len(driver.find_elements_by_css_selector("svg .y_gridlines")) > 0

    helium.go_to(root_url + "/summary/visual/assessment/2/embedded-tableau/")
    helium.wait_until(helium.Text("embedded-tableau").exists)
    helium.wait_until(helium.S(".tableauPlaceholder iframe").exists, timeout_secs=20)
    assert len(driver.find_elements_by_tag_name("iframe")) > 0

    helium.go_to(root_url + "/summary/visual/assessment/2/rob-heatmap/")
    helium.wait_until(helium.Text("rob-heatmap").exists)
    helium.wait_until(helium.S("svg.d3").exists)
    assert len(driver.find_elements_by_css_selector("svg .legend")) > 0

    helium.go_to(root_url + "/summary/visual/assessment/2/tagtree/")
    helium.wait_until(helium.Text("Human Study").exists)
    helium.wait_until(helium.S("svg.d3").exists)
    assert len(driver.find_elements_by_css_selector("svg .tagnode")) == 4

    helium.go_to(root_url + "/summary/visual/assessment/2/exploratory-heatmap/")
    helium.wait_until(helium.Text("exploratory-heatmap").exists)
    helium.wait_until(helium.S("svg.d3").exists)
    assert len(driver.find_elements_by_css_selector("svg.d3 g rect")) > 5

    helium.go_to(root_url + "/summary/visual/assessment/2/bioassay-aggregation/")
    helium.wait_until(helium.Text("bioassay-aggregation").exists)
    helium.wait_until(helium.S("svg.d3").exists)
    assert len(driver.find_elements_by_css_selector("svg.d3 g circle")) > 5


def _check_tables_working(driver, root_url):
    """
    Tests to ensure all visual types are displayed.
    """
    # check summary table
    helium.go_to(root_url + "/summary/assessment/1/tables/")
    helium.wait_until(helium.Text("Available tables").exists)
    assert len(driver.find_elements_by_css_selector("table tbody tr")) == 3

    # check generic table
    helium.go_to(root_url + "/summary/assessment/1/tables/Generic-1/")
    helium.wait_until(helium.S(".summaryTable").exists)

    # check evidence profile
    helium.go_to(root_url + "/summary/assessment/1/tables/Evidence-Profile-1/")
    helium.wait_until(helium.S(".summaryTable").exists)

    # check study evaluation
    helium.go_to(root_url + "/summary/assessment/1/tables/Study-Evaluation-1/")
    helium.wait_until(helium.S(".summaryTable").exists)


def _check_modals_working(driver, root_url):
    """
    Tests to ensure that modals on visuals are working correctly.
    """
    # check study display modal
    helium.go_to(root_url + "/summary/data-pivot/assessment/2/animal-bioassay-data-pivot-endpoint/")
    helium.wait_until(helium.Text("study name").exists)
    helium.click("Biesemeier JA et al. 2011")
    helium.wait_until(helium.Text("Click on any cell above to view details.").exists)
    shared.click_text(driver, "Show all details")
    assert helium.Text("metric 1").exists()
    assert helium.Text("overall").exists()
    shared.click_text(driver, "Hide all details")
    assert not helium.Text("metric 1").exists()
    assert not helium.Text("overall metric 1").exists()
    shared.click_text(driver, "domain 1")
    assert helium.Text("metric 1").exists()
    assert not helium.Text("overall metric 1").exists()
    shared.click_text(driver, "overall")
    assert not helium.Text("metric 1").exists()
    assert helium.Text("overall metric 1").exists()
    helium.click(helium.S('//button[text()="Close"]'))


def summary(driver, root_url):
    shared.login(root_url)
    _check_exploratory_heatmaps(driver, root_url)
    _check_browsing(driver, root_url)
    _check_visuals_working(driver, root_url)
    _check_tables_working(driver, root_url)
    _check_modals_working(driver, root_url)
    shared.logout()
