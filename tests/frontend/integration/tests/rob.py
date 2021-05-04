import helium as h

from . import shared


def rob(driver, root_url):

    shared.login(root_url)

    # /rob/assessment/:id/
    h.go_to(root_url + "/rob/assessment/1/")
    assert h.Text("example domain Domain").exists() is True
    assert h.Text("final domain Domain").exists() is True
    assert h.Text("example metric").exists() is True

    # /rob/assessment/:id/study-assignments/
    h.go_to(root_url + "/rob/assessment/1/study-assignments/")
    assert len(driver.find_elements_by_css_selector("tr")) > 0
    assert len(driver.find_elements_by_css_selector("td")) > 4
    assert h.Text("Foo et al.", to_left_of="Team Member").exists()

    # /rob/:id/update/
    h.go_to(root_url + "/rob/3/update/")
    h.wait_until(h.Text("example metric").exists)
    assert len(driver.find_elements_by_css_selector(".score-form")) == 3

    # /rob/study/:id/
    h.go_to(root_url + "/rob/study/7/")
    assert h.Text("Biesemeier JA et al. 2011: Risk of bias review").exists() is True
    h.wait_until(h.Text("domain 1").exists)
    assert len(driver.find_elements_by_css_selector(".aggregate-flex")) > 0
    assert len(driver.find_elements_by_css_selector(".aggregate-flex .domain-cell")) == 2

    shared.logout()
