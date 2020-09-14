import helium as h

assessment_url = "/assessment/2/"


def summary_visual_browse(driver, live_server_url):
    """
    Assert we can render the compelted HAWC visualizations. This includes:
    - the visuals list page
    - a data pivot summary page
    - a risk of bias heatmap can be rendered
    - TODO - add other visualization type checks
    """
    # set test to use our session-level driver
    h.set_driver(driver)

    # go to website
    h.go_to(live_server_url + "/summary" + assessment_url + "visuals/")

    assert h.Text("Available visualizations").exists() is True
    h.wait_until(h.Text("Title").exists)
    assert len(driver.find_elements_by_css_selector("tr")) > 10

    h.click("data pivot - animal bioassay - endpoint")
    assert "animal-bioassay-data-pivot-endpoint" in driver.current_url

    # different than requested
    assert h.Link("Actions").exists() is True

    h.wait_until(h.Text("study name").exists)

    # ensure that the image exists
    assert len(driver.find_elements_by_css_selector("#dp_display svg")) > 0

    # ensure that the image has at least 7 circles there has to be a better way to do this
    assert len(driver.find_elements_by_css_selector("#dp_display svg g g path")) > 7

    # click on download link using selenium driver logic because Font Awesome icon is hard for selenium
    driver.find_elements_by_css_selector('a[title="Download figure"]')[0].click()

    # make sure download "button" is visible
    assert h.Text("Download as a SVG").exists() is True

    h.go_to(live_server_url + "/summary" + assessment_url + "visuals/")
    h.wait_until(h.Text("Title").exists)

    # click the heatmap example
    driver.find_element_by_link_text("heatmap").click()

    assert "/summary/visual/3/" in driver.current_url

    # make sure the heatmap loads before doing the following tests
    h.wait_until(h.Text("heatmap").exists)

    assert h.Link("Actions").exists() is False

    # ensure that the image exists
    assert len(driver.find_elements_by_css_selector("svg")) > 0

    # ensure that the image has at least 5 rectangles there has to be a better way to do this
    assert len(driver.find_elements_by_css_selector("svg g rect")) > 5
