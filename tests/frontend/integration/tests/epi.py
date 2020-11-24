import helium as h

from . import shared


def epi(driver, root_url):
    shared.login(root_url)

    # /study-population/:id/
    h.go_to(root_url + "/epi/study-population/1/")
    h.wait_until(h.Text("Case series").exists)
    assert h.Text("Study design").exists() is True
    assert h.Text("Case series").exists() is True
    assert len(driver.find_elements_by_css_selector("li")) > 3

    # /exposure/:id/
    h.go_to(root_url + "/epi/exposure/1/")
    h.wait_until(h.Text("What was measured").exists)
    assert h.Text("What was measured").exists() is True
    assert h.Text("Sarin").exists() is True

    # /comparison-set/:id/
    h.go_to(root_url + "/epi/comparison-set/1/")
    h.wait_until(h.Text("Exposure details").exists)
    assert len(driver.find_elements_by_css_selector("table")) > 0
    assert len(h.find_all(h.S("#groups-table > tbody > tr"))) == 3

    # /outcome/:id/
    h.go_to(root_url + "/epi/outcome/4/")
    h.wait_until(h.Text("Name").exists)
    assert h.Text("Name").exists() is True
    assert h.Text("partial PTSD").exists() is True
    assert len(driver.find_elements_by_css_selector(".nav.nav-tabs")) == 1

    # /result/:id/
    h.go_to(root_url + "/epi/result/1/")
    h.wait_until(h.Text("Comparison set").exists)
    assert len(driver.find_elements_by_css_selector("#objContainer table")) == 2
    assert h.Text("Table 2", to_right_of="Data location").exists()
    assert len(driver.find_elements_by_css_selector("tr")) > 10

    shared.logout()
