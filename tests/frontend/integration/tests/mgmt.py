from urllib.parse import urlparse

import helium as h


def mgmt(driver, root_url):
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

    h.go_to(root_url + "/mgmt/assessment/1/")

    h.wait_until(h.Text("All task summary").exists)

    # assert 6 svg of class .task-chart exist
    assert len(driver.find_elements_by_css_selector("svg.task-chart")) == 6

    h.go_to(root_url + "/mgmt/assessment/1/edit/")

    h.wait_until(h.Text("Sort studies by").exists)

    # assert 6 svg of class .task-chart exist
    assert len(driver.find_elements_by_css_selector(".taskStudy")) == 1

    # logout; cleanup test
    h.click("Your HAWC")
    h.click("Logout")
