import os
from urllib.parse import urlparse

import helium as h
import pytest

SKIP_INTEGRATION = os.environ.get("HAWC_INTEGRATION_TESTS") is None


@pytest.mark.skipif(SKIP_INTEGRATION, reason="integration test")
def test_login(chrome_driver, live_server):

    # set test to use our session-level driver
    h.set_driver(chrome_driver)

    # go to website
    h.go_to(live_server.url)
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
    h.go_to(live_server.url + "/user/login/")
    h.write("pm@pm.com", into="Email*")
    h.write("pw", into="Password*")
    h.click("Login")
    assert urlparse(chrome_driver.current_url).path == "/portal/"
