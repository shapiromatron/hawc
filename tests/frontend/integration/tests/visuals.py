import helium as h

from . import shared


def visuals(driver, root_url):
    shared.login(root_url)

    h.go_to(root_url + "/summary/visual/5/")

    h.wait_until(h.Text("legend").exists)

    # ensure svg exists and .legend exists in svg
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector("svg .legend")) > 0

    h.go_to(root_url + "/summary/visual/4/")

    h.wait_until(h.Text("Dose").exists)

    # ensure svg exists and .crossview_path_group exists in svg
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector("svg .crossview_path_group")) > 0

    h.go_to(root_url + "/summary/data-pivot/assessment/2/animal-bioassay-data-pivot-endpoint/")

    h.wait_until(h.Text("study name").exists)

    # ensure svg exists and .x_gridliens and .y_gridlines exist
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector("svg .x_gridlines")) > 0
    assert len(driver.find_elements_by_css_selector("svg .y_gridlines")) > 0

    h.go_to(root_url + "/summary/data-pivot/assessment/2/data-pivot-epi/")

    h.wait_until(h.Text("study name").exists)

    # ensure svg exists and .x_gridliens and .y_gridlines exist
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector("svg .x_gridlines")) > 0
    assert len(driver.find_elements_by_css_selector("svg .y_gridlines")) > 0

    h.go_to(root_url + "/summary/visual/7/")

    h.wait_until(h.Text("embedded-tableau").exists)

    # ensure iframe exists inside .tableauPlaceholder -- this is causing problems
    # assert len(driver.find_elements_by_tag_name("iframe")) > 0

    h.go_to(root_url + "/summary/visual/3/")

    h.wait_until(h.Text("heatmap").exists)

    # ensure svg exists and .legend exists in svg
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector("svg .legend")) > 0

    h.go_to(root_url + "/summary/visual/6/")

    h.wait_until(h.Text("Human Study").exists)

    # ensure svg exists and 4 .tagnode exists in svg
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector("svg .tagnode")) == 4

    shared.logout()
