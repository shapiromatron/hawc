import helium as h

from . import shared


def literature(driver, root_url):

    shared.login(root_url)

    h.go_to(root_url + "/lit/assessment/2/")
    h.wait_until(h.Text("Inclusion").exists)

    # check that > 5 .nestedTag exist in #tag
    assert len(driver.find_elements_by_css_selector("#tags .nestedTag")) > 5

    # check that if you click "Human Study (2)", two #reference_detail_div exists
    # has proved difficult
    h.click("View By Tag")
    h.wait_until(h.Text("Available references").exists)

    assert "/lit/assessment/2/references/" in driver.current_url

    assert h.Text("Human Study (2)").exists() is True

    assert len(driver.find_elements_by_css_selector("#references_detail_div")) > 0

    # for elem in driver.find_elements_by_css_selector(".nestedTag"):
    #     if "Human Study" in elem.text:
    #         elem.click()
    #         print("clicked")
    #         time.sleep(10)
    #         break

    # h.wait_until(h.Text("References tagged:").exists)

    # h.wait_until(h.Text("Tokyo subway system").exists)

    # assert len(driver.find_elements_by_css_selector("#reference_detail_div")) > 1

    h.go_to(root_url + "/lit/assessment/2/references/visualization/")

    h.wait_until(h.Text("public final").exists)

    # ensure svg exists and 3 .tagnode exists in svg
    assert len(driver.find_elements_by_css_selector("svg")) > 0
    assert len(driver.find_elements_by_css_selector("svg .tagnode")) == 3

    h.go_to(root_url + "/lit/assessment/2/references/search/")

    h.wait_until(h.Text("HAWC ID").exists)

    # add "Kawana" to Authors and search, assert 1 #reference_detail_div exists
    h.write("Kawana", into="Authors")
    h.click("Search")
    h.wait_until(h.Text("1 references found.").exists)
    assert len(driver.find_elements_by_css_selector("#reference_detail_div")) == 1

    shared.logout()
