from urllib.parse import urlparse

import helium as h


def login(chrome_driver, root_url):

    # set test to use our session-level driver
    h.set_driver(chrome_driver)

    # go to website
    h.go_to(root_url)
    h.click("Login")
    assert "/user/login/" in chrome_driver.current_url

    # invalid password check
    msg = "Please enter a correct email and password."
    assert h.Text(msg).exists() is False
    h.write("webmaster@hawcproject.org", into="Email*")
    h.write("not my password", into="Password*")
    h.click("Login")
    assert h.Text(msg).exists() is True
    assert urlparse(chrome_driver.current_url).path == "/user/login/"

    # valid password check
    h.go_to(root_url + "/user/login/")
    h.write("pm@pm.com", into="Email*")
    h.write("pw", into="Password*")
    h.click("Login")
    assert urlparse(chrome_driver.current_url).path == "/portal/"

    # logout; cleanup test
    h.click("Your HAWC")
    h.click("Logout")
