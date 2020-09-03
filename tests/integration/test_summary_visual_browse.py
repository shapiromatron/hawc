import os

import helium as h
import pytest

SKIP_INTEGRATION = os.environ.get("HAWC_INTEGRATION_TESTS") is None

assessment_url = "/assessment/2/"


@pytest.mark.skipif(SKIP_INTEGRATION, reason="integration test")
def test_hello_helium(chrome_driver, live_server):
    # set test to use our session-level driver
    h.set_driver(chrome_driver)

    # go to website
    h.go_to(live_server.url + "/summary" + assessment_url + "visuals/")

    assert h.Text("Available visualizations").exists() is True
    h.wait_until(h.Text("Title").exists)
    assert len(chrome_driver.find_elements_by_css_selector("tr")) > 10

    h.click("data pivot - animal bioassay - endpoint")
    assert "animal-bioassay-data-pivot-endpoint" in chrome_driver.current_url

    # different than requested
    assert h.Link("Actions").exists() is True

    h.wait_until(h.Text("study name").exists)

    # ensure that the image exists
    assert len(chrome_driver.find_elements_by_css_selector("#dp_display svg")) > 0

    # ensure that the image has at least 7 circles there has to be a better way to do this
    assert len(chrome_driver.find_elements_by_css_selector("#dp_display svg g g path")) > 7

    # click on download link using selenium driver logic because Font Awesome icon is hard for selenium
    chrome_driver.find_elements_by_css_selector('a[title="Download figure"]')[0].click()

    # make sure download "button" is visible
    assert h.Text("Download as a SVG").exists() is True

    h.go_to(live_server.url + "/summary" + assessment_url + "visuals/")

    # click the heatmap example
    h.click("heatmap")

    assert "/summary/visual/3/" in chrome_driver.current_url

    # make sure the heatmap loads before doing the following tests
    h.wait_until(h.Text("heatmap").exists)

    assert h.Link("Actions").exists() is False

    # ensure that the image exists
    assert len(chrome_driver.find_elements_by_css_selector("svg")) > 0

    # ensure that the image has at least 5 rectangles there has to be a better way to do this
    assert len(chrome_driver.find_elements_by_css_selector("svg g rect")) > 5
