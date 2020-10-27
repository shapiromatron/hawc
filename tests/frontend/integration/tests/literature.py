import helium as h
import time

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

    # lets assume we need to wait for the js events to be attached to the elements
    # time.sleep(5)

    # h.click("Human Study (2)")

    # print(h.Text("Human Study (2)").value)

    # TODO: I've tried every method of clicking on Human Study(2) that I can find it's like the click event isn't bound
    # for elem in driver.find_elements_by_css_selector(".nestedTag"):
    #     if "Human Study" in elem.text:
    #         driver.execute_script("arguments[0].click();", elem)
    #         print("clicked")
    #         break

    # h.wait_until(h.Text("References tagged:").exists, 30)

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
