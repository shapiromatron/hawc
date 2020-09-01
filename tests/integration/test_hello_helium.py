import os

import helium as h
import pytest

SKIP_INTEGRATION = os.environ.get("HAWC_INTEGRATION_TESTS") is None


@pytest.mark.skipif(SKIP_INTEGRATION, reason="integration test")
def test_hello_helium(chrome_driver, live_server):
    print(live_server.url)
    # set test to use our session-level driver
    h.set_driver(chrome_driver)

    # go to website
    h.go_to("https://hawcproject.org")
    h.click("Login")
    assert "/user/login/" in chrome_driver.current_url

    # invalid password check
    msg = "Please enter a correct email and password."
    assert h.Text(msg).exists() is False
    h.write("webmaster@hawcproject.org", into="Email*")
    h.write("not my password", into="Password*")
    h.click("Login")
    assert h.Text(msg).exists() is True


@pytest.mark.skipif(SKIP_INTEGRATION, reason="integration test")
def test_local(chrome_driver, live_server):
    print(live_server.url)
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
