import os

import helium as h
import pytest
from django.test import LiveServerTestCase

SKIP_INTEGRATION = os.environ.get("HAWC_INTEGRATION_TESTS") is None


class SeleniumTest(LiveServerTestCase):
    @pytest.mark.skipif(SKIP_INTEGRATION, reason="integration test")
    def test_hello_helium(self, chrome_driver):
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
    def test_local(self, chrome_driver):
        # set test to use our session-level driver
        h.set_driver(chrome_driver)

        # go to website
        h.go_to("http://web-server")
        h.click("Login")
        assert "/user/login/" in chrome_driver.current_url

        # invalid password check
        msg = "Please enter a correct email and password."
        assert h.Text(msg).exists() is False
        h.write("webmaster@hawcproject.org", into="Email*")
        h.write("not my password", into="Password*")
        h.click("Login")
        assert h.Text(msg).exists() is True
