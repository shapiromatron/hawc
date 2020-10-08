from urllib.parse import urlparse

import helium as h


def bioassay(driver, root_url):

    h.go_to(root_url + "/user/login/")
    h.write("pm@pm.com", into="Email*")
    h.write("pw", into="Password*")
    h.click(h.S("@login"))

    print(driver.current_url)
    assert (
        h.Text(
            "Please enter a correct email and password. Note that both fields may be case-sensitive."
        ).exists()
        is False
    )
    assert urlparse(driver.current_url).path == "/portal/"

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

    # logout; cleanup test
    h.click("Your HAWC")
    h.click("Logout")
