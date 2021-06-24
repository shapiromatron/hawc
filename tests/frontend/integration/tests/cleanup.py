import helium as h

from . import shared


def cleanup(driver, root_url):
    shared.login(root_url)

    # /assessment/:id/clean-extracted-data/
    h.go_to(root_url + "/assessment/1/clean-extracted-data/")
    h.wait_until(h.Text("Cleanup Chemical Z").exists)
    h.click("1 animal bioassay endpoints")
    h.wait_until(h.Text("Cleanup Animal Bioassay Endpoints").exists)
    h.click("system")
    h.wait_until(h.Text("Cleanup Animal Bioassay Endpoints → System").exists)
    h.write("test", into=h.S("@system"))
    match_text = "test (1)"
    assert h.Text(match_text).exists() is False
    h.click("Submit bulk edit")
    h.wait_until(h.Text(match_text).exists)
    h.write("N/A", into=h.S("@system"))
    match_text = "N/A (1)"
    assert h.Text(match_text).exists() is False
    h.click("Submit bulk edit")
    h.wait_until(h.Text(match_text).exists)

    # /assessment/:id/clean-study-metrics/
    h.go_to(root_url + "/assessment/1/clean-study-metrics/")
    h.wait_until(h.Text("Select the metric to edit").exists)
    assert len(h.find_all(h.S(".checkbox-score-display-row"))) == 0
    h.click("Load responses")
    h.wait_until(h.Text("met your criteria:").exists)
    assert len(h.find_all(h.S(".checkbox-score-display-row"))) == 1
    h.click(h.S("@checkbox-score-select", below="Foo et al."))
    h.select(h.ComboBox(below="Score"), "Not reported")
    h.click(h.S('.bulkEditForm button[type="button"].btn-primary'))
    h.wait_until(lambda: len(h.find_all(h.S(".bulkEditForm"))) == 0)
    assert "Not reported" in driver.find_elements_by_css_selector(".score-bar i")[0].text
    h.click(h.S("@checkbox-score-select", below="Foo et al."))
    h.select(h.ComboBox(below="Score"), "Probably low risk of bias")
    h.click(h.S('.bulkEditForm button[type="button"].btn-primary'))
    h.wait_until(lambda: len(h.find_all(h.S(".bulkEditForm"))) == 0)
    assert (
        "Probably low risk of bias" in driver.find_elements_by_css_selector(".score-bar i")[0].text
    )

    shared.logout()
