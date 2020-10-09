import helium as h

from . import shared


def heatmap_builtins(driver, root_url):
    shared.login(root_url)

    h.go_to(root_url + "/assessment/2/endpoints/")

    # ensure that the first two columns say "Bioassay" and "Epidemiology" and the table is 3x4
    assert len(driver.find_elements_by_css_selector("tr")) == 3
    assert len(driver.find_elements_by_css_selector("td")) == 8

    assert h.Text(below="Data type").value == "Bioassay"
    assert h.Text(below="Bioassay").value == "Epidemiology"

    h.go_to(root_url + "/ani/assessment/2/heatmap-study-design/")

    # having timing issues here
    h.wait_until(condition_fn=h.Text("Grand Total").exists, timeout_secs=60)

    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector(".exp_heatmap_cell")) == 4

    shared.logout()
