from urllib.parse import urlparse

import helium as h


def login(root_url: str):
    h.go_to(root_url + "/user/login/")
    h.write("pm@hawcproject.org", into="Email*")
    h.write("pw", into="Password*")
    h.click(h.S("@login"))
    h.wait_until(condition_fn=lambda: urlparse(h.get_driver().current_url).path == "/portal/")
    assert h.Text("Your HAWC").exists()


def logout():
    h.click("Your HAWC")
    h.click("Logout")
    assert h.Text("Your HAWC").exists() is False
    assert urlparse(h.get_driver().current_url).path == "/"


def click_text(driver, text: str):
    """
    Helium has trouble clicking elements that are scrolled off screen.
    This uses the webdriver directly instead.
    """
    driver.find_element_by_xpath(f'//*[text()="{text}"]').click()
