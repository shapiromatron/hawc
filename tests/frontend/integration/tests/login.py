from urllib.parse import urlparse

import helium as h


def login(driver, root_url):
    """
    Assert that we're able to login/logout successfully and an errors are displayed as expected.
    """
    # set test to use our session-level driver
    h.set_driver(driver)

    # go to website
    h.go_to(root_url)
    assert h.Link("Login").exists() is True
    h.click("Login")
    assert "/user/login/" in driver.current_url

    # invalid password check
    msg = "Please enter a correct email and password."
    assert h.Text(msg).exists() is False
    h.write("webmaster@hawcproject.org", into="Email*")
    h.write("not my password", into="Password*")

    # changed to target the specific login button in the form seems
    # there was some randomness in whether it clicked the right button/lnk
    h.click(h.S("@login"))
    assert h.Text(msg).exists() is True
    assert urlparse(driver.current_url).path == "/user/login/"

    # valid password check
    h.go_to(root_url + "/user/login/")
    h.write("pm@pm.com", into="Email*")
    h.write("pw", into="Password*")
    # changed to target the specific login button in the form seems
    # there was some randomness in whether it clicked the right button/lnk
    h.click(h.S("@login"))
    assert urlparse(driver.current_url).path == "/portal/"

    # logout; cleanup test
    h.click("Your HAWC")
    h.click("Logout")
