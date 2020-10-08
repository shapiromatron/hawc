from urllib.parse import urlparse

import helium as h


def rob(driver, root_url):

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

    h.go_to(root_url + "/rob/assessment/1/")

    # check that "example domain Domain" and "final domain Domain" headers exist
    assert h.Text("example domain Domain").exists() is True
    assert h.Text("final domain Domain").exists() is True

    # check that "example metric" exists
    assert h.Text("example metric").exists() is True

    h.go_to(root_url + "/rob/assessment/1/study-assignments/")

    # ensure there is 1 row with Foo et al. and 4 columns
    assert len(driver.find_elements_by_css_selector("tr")) > 0

    assert len(driver.find_elements_by_css_selector("td")) > 4

    assert h.Text(to_left_of="Team Member").value == "Foo et al."

    h.go_to(root_url + "/rob/3/edit/")

    h.wait_until(h.Text("example metric").exists)

    # ensure that there are 3 .score-form
    assert len(driver.find_elements_by_css_selector(".score-form")) == 3

    # logout; cleanup test
    h.click("Your HAWC")
    h.click("Logout")
