import helium as h

from . import shared


def study(driver, root_url):

    shared.login(root_url)

    # /study/assessment/:id/
    h.go_to(root_url + "/study/assessment/2/")
    h.wait_until(h.Text("Short citation").exists)
    # 4 (1 per study) + 1 (header row) + 1 (hidden row for correct table striping) == 6
    assert len(driver.find_elements_by_css_selector("tbody tr")) == 6

    # /study/:id/
    h.go_to(root_url + "/study/7/")
    h.wait_until(h.Text("Animal bioassay").exists)
    h.wait_until(h.Link("PubMed").exists)
    assert h.Text("Biesemeier JA et al. 2011").exists() is True
    assert h.Link("PubMed").exists() is True
    assert h.Link("Actions").exists() is False
    assert len(driver.find_elements_by_css_selector("#study_details")) > 0
    assert len(driver.find_elements_by_css_selector("table")) > 0
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    has_data_entry = False
    for elem in driver.find_elements_by_css_selector("th"):
        if "Data type(s)" in elem.text:
            has_data_entry = True
            break
    assert has_data_entry is True

    shared.logout()
