import helium as h

from . import shared


def cleanup(driver, root_url):
    shared.login(root_url)

    # clean extracted data
    h.go_to(root_url + "/assessment/1/clean-extracted-data/")
    h.wait_until(h.Text("Cleanup working").exists)
    h.click("1 animal bioassay endpoints")
    h.wait_until(h.Text("Cleanup Animal Bioassay Endpoints").exists)
    h.click("system")
    h.wait_until(h.Text("Cleanup Animal Bioassay Endpoints → System").exists)
    h.write("test", into=h.S("@system"))
    match_text = "test (1)"
    assert h.Text(match_text).exists() is False
    h.click("Submit bulk edit")
    h.wait_until(h.Text(match_text).exists)

    # clean risk of bias
    h.go_to(root_url + "/assessment/1/clean-study-metrics/")
    h.wait_until(h.Text("Select the metric to edit").exists)
    assert len(h.find_all(h.S(".checkbox-score-display-row"))) == 0
    h.click("Load responses")
    h.wait_until(h.Text("Responses which meet your filtered criteria above:").exists)
    assert len(h.find_all(h.S(".checkbox-score-display-row"))) == 1
    h.click(h.S("@checkbox-score-select", below="Foo et al."))
    h.select(h.ComboBox(below="Score"), "Not reported")
    h.click("Bulk modify 1 item.")
    h.wait_until(h.Text("Not reported", to_right_of="Foo et al.").exists)

    shared.logout()
