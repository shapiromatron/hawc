from urllib.parse import urlparse

import helium as h

from . import shared


def login(driver, root_url):
    """
    Assert that we're able to login/logout successfully and an errors are displayed as expected.
    """
    h.go_to(root_url)
    assert h.Link("Login").exists() is True
    h.click("Login")
    assert "/user/login/" in driver.current_url

    # invalid password check
    msg = "Please enter a correct email and password."
    assert h.Text(msg).exists() is False
    h.write("admin@hawcproject.org", into="Email*")
    h.write("not my password", into="Password*")

    # changed to target the specific login button in the form seems
    # there was some randomness in whether it clicked the right button/lnk
    h.click(h.S("@login"))
    assert h.Text(msg).exists() is True
    assert urlparse(driver.current_url).path == "/user/login/"

    # confirm correct login
    shared.login(root_url)
    assert urlparse(driver.current_url).path == "/portal/"

    # confirm logout
    shared.logout()
    assert urlparse(driver.current_url).path == "/"
