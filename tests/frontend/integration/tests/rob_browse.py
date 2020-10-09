import helium as h


def rob_browse(driver, live_server_url):
    """
    Assert that we can view study-level risk of bias pages, and rich content. This includes:
    - the study summary + risk of bias donut plot
    - the study + risk of bias detail page and visualization
    """
    # go to website
    h.go_to(live_server_url + "/study/7/")

    studyTitle = "Biesemeier JA et al. 2011"

    assert h.Text(studyTitle).exists() is True

    # wait for the DOM load
    h.wait_until(h.Link("PubMed").exists)

    # no available HERO links to test in any of the studies I found in the unit-test framework
    assert h.Link("PubMed").exists() is True

    # should not have an Actions link
    assert h.Link("Actions").exists() is False

    # make sure we have an SVG on the page
    assert len(driver.find_elements_by_css_selector("svg")) > 0

    h.go_to(live_server_url + "/rob/study/7/")

    assert h.Text(studyTitle + ": Risk of bias review").exists() is True

    # wait for DOM load
    h.wait_until(h.Text("domain 1").exists)

    # make sure we have an aggregate-flex class
    assert len(driver.find_elements_by_css_selector(".aggregate-flex")) > 0

    # make sure we have x amount of cells
    assert len(driver.find_elements_by_css_selector(".aggregate-flex .domain-cell")) == 2
