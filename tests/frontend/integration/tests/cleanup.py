import helium as h

from . import shared


def cleanup(driver, root_url):
    shared.login(root_url)

    # clean extracted data
    h.go_to(root_url + "/assessment/1/clean-extracted-data/")
    h.wait_until(h.Text("Cleanup working").exists)
    h.click("1 animal bioassay endpoints")
    h.wait_until(h.Text("Cleanup field selection for Animal bioassay endpoints").exists)
    h.click("System")
    h.wait_until(h.Text("System edit").exists)

    # TODO need more classes

    # clean risk of bias
    h.go_to(root_url + "/assessment/1/clean-study-metrics/")
    h.wait_until(h.Text("Select the metric to edit").exists)
    h.click("Load responses")
    h.wait_until(h.Text("Responses which meet your filtered criteria above:").exists)

    # TODO need more classes

    shared.logout()
