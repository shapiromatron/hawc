import helium as h

from . import shared


def bioassay(driver, root_url):
    shared.login(root_url)

    # /experiment/
    h.go_to(root_url + "/ani/experiment/1/")
    h.wait_until(h.Text("Multiple generations").exists)

    assert len(driver.find_elements_by_css_selector("#objContainer table")) > 0

    hasValueInTable = False

    # confirm #objContainer > table > contains "2 year bioassay" in table
    for elem in driver.find_elements_by_css_selector("#objContainer table td"):
        if "2 year bioassay" in elem.text:
            hasValueInTable = True
            break

    assert hasValueInTable

    # confirm "tester" exists under Available animal groups
    assert h.Text(to_left_of="rat").value == "tester"

    # /animal-group/
    h.go_to(root_url + "/ani/animal-group/1/")
    h.wait_until(h.Text("Dosing regime").exists)

    # confirm "sprague dawley" text exists in table
    assert h.Text("sprague dawley").exists() == True
    # confirm "Oral diet" text exists in table
    assert h.Text("Oral diet").exists() == True
    # confirm "mg/kg/d" text exists
    assert h.Text("mg/kg/d").exists() == True
    # confirm "my outcome" test exists
    assert h.Text("my outcome").exists() == True

    # TODO: /endpoint/
    h.go_to(root_url + "/ani/endpoint/1/")
    h.wait_until(h.Text("my outcome").exists)

    # ensure LOEL -> 100 mg/kg/d exists
    assert "100 mg/kg/d" in h.Text(to_right_of="LOEL").value
    # ensure svg plot exists, and .d3 .dr_dots .dose_points == 3
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector(".d3 .dr_dots .dose_points")) == 3
    # ensure #dr-tbl exists and there are 4 rows in it - 5 because of the footer
    assert len(driver.find_elements_by_css_selector("#dr-tbl")) > 0
    assert len(driver.find_elements_by_css_selector("#dr-tbl tr")) == 5

    shared.logout()
