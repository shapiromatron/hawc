from urllib.parse import urlparse

import helium as h


def study(driver, root_url):

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

    h.go_to(root_url + "/study/assessment/2/")

    h.wait_until(h.Text("Short citation").exists)

    # confirm 4 rows exist in table tbody
    assert len(driver.find_elements_by_css_selector("tbody tr")) == 4

    h.go_to(root_url + "/study/7/")

    h.wait_until(h.Text("Animal bioassay").exists)

    # confirm #study_details exists
    assert len(driver.find_elements_by_css_selector("#study_details")) > 0

    # confirm table exists
    assert len(driver.find_elements_by_css_selector("table")) > 0

    hasDataTypeEntry = False

    # in a column says Data type(s)
    for elem in driver.find_elements_by_css_selector("th"):
        if "Data type(s)" in elem.text:
            hasDataTypeEntry = True
            break

    assert hasDataTypeEntry

    # logout; cleanup test
    h.click("Your HAWC")
    h.click("Logout")
