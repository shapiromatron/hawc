import helium as h

from . import shared


def bioassay(driver, root_url):
    shared.login(root_url)

    # /experiment/:id/
    h.go_to(root_url + "/ani/experiment/1/")
    h.wait_until(h.Text("Multiple generations").exists)
    assert len(driver.find_elements_by_css_selector("#objContainer table")) > 0
    in_table = False
    for elem in driver.find_elements_by_css_selector("#objContainer table td"):
        if "2 year bioassay" in elem.text:
            in_table = True
            break
    assert in_table is True
    assert len(h.find_all(h.S("#ag-table tbody tr"))) == 1

    # /animal-group/:id/
    h.go_to(root_url + "/ani/animal-group/1/")
    h.wait_until(h.Text("Dosing regime").exists)
    assert h.Text("sprague dawley").exists()
    assert h.Text("Oral diet").exists()
    assert h.Text("0, 10, 100 mg/kg/d").exists()
    assert h.Text("my outcome").exists()

    # /endpoint/:id/
    h.go_to(root_url + "/ani/endpoint/1/")
    h.wait_until(h.Text("my outcome").exists)
    assert h.Text("100 mg/kg/d", to_right_of="LOEL").exists()
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector(".d3 .dr_dots .dose_points")) == 3
    assert len(driver.find_elements_by_css_selector("#dr-tbl")) > 0
    assert len(driver.find_elements_by_css_selector("#dr-tbl tr")) == 5

    shared.logout()
