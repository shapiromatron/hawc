from urllib.parse import urlparse

import helium as h


def epi(driver, root_url):
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

    h.go_to(root_url + "/epi/study-population/1/")

    h.wait_until(h.Text("Case series").exists)

    # Ensure "Study design" and "Case series" exist
    assert h.Text("Study design").exists() is True
    assert h.Text("Case series").exists() is True

    # Ensure 1 bullet in each list of Outcome, comparison set, and exposure metric
    assert len(driver.find_elements_by_css_selector("li")) > 3

    h.go_to(root_url + "/epi/exposure/1/")

    h.wait_until(h.Text("What was measured").exists)

    # ensure "What was measured" and "Sarin" in table
    assert h.Text("What was measured").exists() is True
    assert h.Text("Sarin").exists() is True

    h.go_to(root_url + "/epi/comparison-set/1/")

    h.wait_until(h.Text("Exposure details").exists)

    # ensure exposure table exists
    assert len(driver.find_elements_by_css_selector("table")) > 0

    # ensure 3 groups described in exposure set TODO need better classes
    # TODO

    h.go_to(root_url + "/epi/outcome/4/")

    h.wait_until(h.Text("Name").exists)

    # ensure "Name" and "partial PTSD" exist
    assert h.Text("Name").exists() is True
    assert h.Text("partial PTSD").exists() is True

    # ensure .nav .nav-tabs has 1 result
    assert len(driver.find_elements_by_css_selector(".nav.nav-tabs")) == 1

    h.go_to(root_url + "/epi/result/1/")

    h.wait_until(h.Text("Comparison set").exists)

    # ensure two tables in objContainer
    assert len(driver.find_elements_by_css_selector("#objContainer table")) == 2

    # ensure first has "Table 2" text in it
    assert h.Text(to_right_of="Data location").value == "Table 2"

    # ensure second has 3 groups in tbody portion
    assert len(driver.find_elements_by_css_selector("tr")) > 10

    # logout; cleanup test
    h.click("Your HAWC")
    h.click("Logout")
