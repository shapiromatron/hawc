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

    # TODO: /animal-group/
    # TODO: /endpoint/

    shared.logout()
