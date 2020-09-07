import os
from urllib.parse import urlparse

import helium as h
import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase

from . import tests

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


@pytest.mark.skipif(1 == 1, reason="integration test")
@pytest.mark.usefixtures("set_chrome_driver")
class SkipTestIntegration(StaticLiveServerTestCase, TestCase):
    """
    We use a single class that inherits from both StaticLiveServerTestCase and TestCase
    in order to supersede properties of StaticLiveServerTestCase that cause the database to be
    flushed after every test, while still being able to utilize a live server for HTTP requests.

    Further reading: https://code.djangoproject.com/ticket/23640#comment:3
    """

    host = os.environ.get("LIVESERVER_HOST", "localhost")
    port = int(os.environ.get("LIVESERVER_PORT", 0))

    def test_login(self):
        tests.login(self.chrome_driver, self.live_server_url)

    def test_rob_browse(self):
        tests.rob_browse(self.chrome_driver, self.live_server_url)

    def test_summary_visual_browse(self):
        tests.summary_visual_browse(self.chrome_driver, self.live_server_url)

    def test_user_permissions(self):
        tests.user_permissions(self.chrome_driver, self.live_server_url)
