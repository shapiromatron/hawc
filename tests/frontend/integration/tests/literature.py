import helium as h

from . import shared


def literature(driver, root_url):

    shared.login(root_url)

    # /lit/assessment/:id/
    h.go_to(root_url + "/lit/assessment/2/")
    h.wait_until(h.Text("Inclusion").exists)
    assert len(driver.find_elements_by_css_selector("#tags .nestedTag")) > 5

    # /lit/assessment/:id/references/
    h.click("View By Tag")
    h.wait_until(h.Text("Available references").exists)
    h.wait_until(h.S(".nestedTag").exists)
    assert "/lit/assessment/2/references/" in driver.current_url
    assert h.Text("Human Study (2)").exists() is True
    assert len(driver.find_elements_by_css_selector("#references_detail_div")) > 0
    h.click("Human Study (2)")
    h.wait_until(h.Text("2 references tagged:").exists)
    h.wait_until(h.S("#references_detail_div").exists)
    assert len(driver.find_elements_by_css_selector(".referenceDetail")) == 2

    # /lit/assessment/:id/references/visualization/
    h.go_to(root_url + "/lit/assessment/2/references/visualization/")
    h.wait_until(h.Text("Chemical X").exists)
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector("svg .tagnode")) == 3

    # /lit/assessment/:id/references/search/
    h.go_to(root_url + "/lit/assessment/2/references/search/")
    h.wait_until(h.Text("HAWC ID").exists)
    h.write("Kawana", into="Authors")
    h.click("Search")
    h.wait_until(h.Text("1 references found.").exists)
    assert len(driver.find_elements_by_css_selector(".referenceDetail")) == 1

    shared.logout()
