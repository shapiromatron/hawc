import helium as h

from . import shared


def mgmt(driver, root_url):
    shared.login(root_url)

    # /mgmt/assessment/:id/
    h.go_to(root_url + "/mgmt/assessment/1/")
    h.wait_until(h.Text("All task summary").exists)
    assert len(driver.find_elements_by_css_selector("div.barAll")) == 1
    assert len(driver.find_elements_by_css_selector("div.barTask")) == 4
    assert len(driver.find_elements_by_css_selector("div.barUser")) == 1

    # /mgmt/assessment/:id/details/
    h.go_to(root_url + "/mgmt/assessment/1/details/")
    h.wait_until(h.Text("Sort studies by").exists)
    assert len(driver.find_elements_by_css_selector(".taskStudyRow")) == 1

    shared.logout()
