import os

import helium as h
import pytest

SKIP_INTEGRATION = os.environ.get("HAWC_INTEGRATION_TESTS") is None


@pytest.mark.skipif(SKIP_INTEGRATION, reason="integration test")
def test_user_permissions(chrome_driver, live_server):
    # set test to use our session-level driver
    h.set_driver(chrome_driver)

    # go to website
    h.go_to(live_server.url + "/study/7/")

    studyTitle = "Biesemeier JA et al. 2011"

    assert h.Text(studyTitle).exists() is True

    # wait for the DOM load
    h.wait_until(h.Link("PubMed").exists)

    # no available HERO links to test in any of the studies I found in the unit-test framework
    assert h.Link("PubMed").exists() is True

    # should not have an Actions link
    assert h.Link("Actions").exists() is False

    # make sure we have an SVG on the page
    assert len(chrome_driver.find_elements_by_css_selector("svg")) > 0

    h.go_to(live_server.url + "/rob/study/7/")

    assert h.Text(studyTitle + ": Risk of bias review").exists() is True

    # wait for DOM load
    h.wait_until(h.Text("domain 1").exists)

    # make sure we have an aggregate-flex class
    assert len(chrome_driver.find_elements_by_css_selector(".aggregate-flex")) > 0

    # make sure we have x amount of cells
    assert len(chrome_driver.find_elements_by_css_selector(".aggregate-flex .domain-cell")) == 2
