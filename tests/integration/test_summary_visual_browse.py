import os

import helium as h
import pytest

SKIP_INTEGRATION = os.environ.get("HAWC_INTEGRATION_TESTS") is None

base_url = "http://localhost:8000"
assessment_url = "/assessment/2/"

@pytest.mark.skipif(SKIP_INTEGRATION, reason="integration test")
def test_hello_helium(chrome_driver):
    # set test to use our session-level driver
    h.set_driver(chrome_driver)

    # go to website
    h.go_to(base_url + "/summary" + assessment_url + "visuals/")
    # need to figure out how to touch base selenium objects to confirm placement
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


    # Need to close menu on local
    # h.click("Hide")
    # this is too hard to do using helium because of the font-awesome download icon
    # there is technically a better way to do this leveraging expected_conditions, 
    # but because of the selector I'm using to select this download button, it gets messy
    # chrome_driver.implicitly_wait(1) - this didn't even end up working seems like sizing is weird in headless
    # so this generates an error on localhost because of sizing seemingly, because of the 
    # admin help menu, so I'm going to create a hacky javascript way to do this

    downloadElem = chrome_driver.find_elements_by_css_selector("a[title=\"Download figure\"]")[0]
    chrome_driver.execute_script("arguments[0].click();", downloadElem)

    # make sure download "button" is visible
    assert h.Text("Download as a SVG").exists() is True


    h.go_to(base_url + "/summary" + assessment_url + "visuals/")

    #click the heatmap example
    h.click("heatmap")

    assert "/summary/visual/3/" in chrome_driver.current_url

    assert h.Link("Actions").exists() is False

    # ensure that the image exists
    assert len(chrome_driver.find_elements_by_css_selector("svg")) > 0

    # ensure that the image has at least 5 rectangles there has to be a better way to do this
    assert len(chrome_driver.find_elements_by_css_selector("svg g rect")) > 5