import helium as h

from . import shared


def _check_exploratory_heatmaps(driver, root_url):
    """
    Assert we have a list of built-in exploratory heatmap tables and they render.
    """
    # /assessment/:id/endpoints/
    h.go_to(root_url + "/assessment/2/endpoints/")
    assert len(driver.find_elements_by_css_selector("tr")) == 3
    assert len(driver.find_elements_by_css_selector("td")) == 8
    assert h.Text(below="Data type").value == "Bioassay"
    assert h.Text(below="Bioassay").value == "Epidemiology"

    # /ani/assessment/:id/heatmap-study-design/
    h.go_to(root_url + "/ani/assessment/2/heatmap-study-design/")
    h.wait_until(condition_fn=h.Text("Grand Total").exists, timeout_secs=60)
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector(".exp_heatmap_cell")) == 6


def _check_browsing(driver, root_url):
    """
    Assert we can render the completed HAWC visualizations. This includes:

    - the visuals list page
    - a data pivot summary page
    - a risk of bias heatmap can be rendered
    """

    assessment_url = "/assessment/2/"

    # go to website
    h.go_to(root_url + "/summary" + assessment_url + "visuals/")
    assert h.Text("Available visualizations").exists() is True
    h.wait_until(h.Text("Title").exists)
    assert len(driver.find_elements_by_css_selector("tr")) > 10

    # view data pivot
    h.click("data pivot - animal bioassay - endpoint")
    assert "animal-bioassay-data-pivot-endpoint" in driver.current_url
    assert h.Link("Actions").exists() is True
    h.wait_until(h.Text("study name").exists)
    assert len(driver.find_elements_by_css_selector("#dp_display svg")) > 0
    assert len(driver.find_elements_by_css_selector("#dp_display svg g g path")) > 7
    driver.find_elements_by_css_selector('a[title="Download figure"]')[0].click()
    assert h.Text("Download as a SVG").exists() is True

    # view browse again
    h.go_to(root_url + "/summary" + assessment_url + "visuals/")
    h.wait_until(h.Text("Title").exists)

    # click the rob heatmap example
    driver.find_element_by_link_text("rob-heatmap").click()
    assert "rob-heatmap" in driver.current_url
    h.wait_until(h.Text("rob-heatmap").exists)
    assert h.Link("Actions").exists() is False
    assert len(driver.find_elements_by_css_selector("svg.d3")) > 0
    assert len(driver.find_elements_by_css_selector("svg.d3 g rect")) > 5


def _check_visuals_working(driver, root_url):
    """
    Tests to ensure all visual types are displayed.
    """
    h.go_to(root_url + "/summary/visual/5/")
    # visual id should redirect to slug url
    h.wait_until(lambda: "/summary/visual/assessment/2/barchart/" in driver.current_url)
    h.wait_until(h.Text("legend").exists)
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector("svg .legend")) > 0

    h.go_to(root_url + "/summary/visual/assessment/2/crossview/")
    h.wait_until(h.Text("Dose").exists)
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector("svg .crossview_path_group")) > 0

    h.go_to(root_url + "/summary/data-pivot/assessment/2/animal-bioassay-data-pivot-endpoint/")
    h.wait_until(h.Text("study name").exists)
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector("svg .x_gridlines")) > 0
    assert len(driver.find_elements_by_css_selector("svg .y_gridlines")) > 0

    h.go_to(root_url + "/summary/data-pivot/assessment/2/data-pivot-epi/")
    h.wait_until(h.Text("study name").exists)
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector("svg .x_gridlines")) > 0
    assert len(driver.find_elements_by_css_selector("svg .y_gridlines")) > 0

    h.go_to(root_url + "/summary/visual/assessment/2/embedded-tableau/")
    h.wait_until(h.Text("embedded-tableau").exists)
    h.wait_until(h.S(".tableauPlaceholder iframe").exists, timeout_secs=20)
    assert len(driver.find_elements_by_tag_name("iframe")) > 0

    h.go_to(root_url + "/summary/visual/assessment/2/rob-heatmap/")
    h.wait_until(h.Text("rob-heatmap").exists)
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector("svg .legend")) > 0

    h.go_to(root_url + "/summary/visual/assessment/2/tagtree/")
    h.wait_until(h.Text("Human Study").exists)
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector("svg .tagnode")) == 4

    h.go_to(root_url + "/summary/visual/assessment/2/exploratory-heatmap/")
    h.wait_until(h.Text("exploratory-heatmap").exists)
    assert len(driver.find_elements_by_css_selector("svg.d3")) > 0
    assert len(driver.find_elements_by_css_selector("svg.d3 g rect")) > 5

    h.go_to(root_url + "/summary/visual/assessment/2/bioassay-aggregation/")
    h.wait_until(h.Text("bioassay-aggregation").exists)
    assert len(driver.find_elements_by_css_selector("svg.d3")) > 0
    assert len(driver.find_elements_by_css_selector("svg.d3 g circle")) > 5


def visuals(driver, root_url):
    shared.login(root_url)
    _check_exploratory_heatmaps(driver, root_url)
    _check_browsing(driver, root_url)
    _check_visuals_working(driver, root_url)
    shared.logout()
