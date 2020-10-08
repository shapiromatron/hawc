from urllib.parse import urlparse

import helium as h


def cleanup(driver, root_url):
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

    h.go_to(root_url + "/assessment/1/clean-extracted-data/")

    h.wait_until(h.Text("Cleanup working").exists)

    h.click("1 animal bioassay endpoints")

    h.wait_until(h.Text("Cleanup field selection for Animal bioassay endpoints").exists)

    h.click("System")

    h.wait_until(h.Text("System edit").exists)

    # TODO need more classes

    h.go_to(root_url + "/assessment/1/clean-study-metrics/")

    h.wait_until(h.Text("Select the metric to edit").exists)

    h.click("Load responses")

    h.wait_until(h.Text("Responses which meet your filtered criteria above:").exists)

    # TODO need more classes

    # logout; cleanup test
    h.click("Your HAWC")
    h.click("Logout")
