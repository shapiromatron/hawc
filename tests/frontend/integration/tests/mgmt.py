import helium as h

from . import shared


def mgmt(driver, root_url):
    shared.login(root_url)

    # /mgmt/assessment/:id/
    h.go_to(root_url + "/mgmt/assessment/1/")
    h.wait_until(h.Text("All task summary").exists)
    assert len(driver.find_elements_by_css_selector("svg.task-chart")) == 6

    # /mgmt/assessment/:id/update/
    h.go_to(root_url + "/mgmt/assessment/1/update/")
    h.wait_until(h.Text("Sort studies by").exists)
    assert len(driver.find_elements_by_css_selector(".taskStudyRow")) == 1

    shared.logout()
