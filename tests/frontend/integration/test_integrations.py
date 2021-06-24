import os

import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase

from . import tests

SKIP_INTEGRATION = os.environ.get("HAWC_INTEGRATION_TESTS") is None
BROWSER = os.environ.get("BROWSER", "firefox")  # default to firefox; seems more stable


@pytest.mark.skipif(SKIP_INTEGRATION, reason="integration test")
@pytest.mark.usefixtures("set_firefox_driver" if BROWSER == "firefox" else "set_chrome_driver")
class TestIntegration(StaticLiveServerTestCase, TestCase):
    """
    We use a single class that inherits from both StaticLiveServerTestCase and TestCase
    in order to supersede properties of StaticLiveServerTestCase that cause the database to be
    flushed after every test, while still being able to utilize a live server for HTTP requests.

    Further reading: https://code.djangoproject.com/ticket/23640#comment:3
    """

    host = os.environ.get("LIVESERVER_HOST", "localhost")
    port = int(os.environ.get("LIVESERVER_PORT", 0))

    # basic functionality
    def test_login(self):
        tests.login(self.driver, self.live_server_url)

    def test_user_permissions(self):
        tests.user_permissions(self.driver, self.live_server_url)

    # domain-specific apps
    def test_literature(self):
        tests.literature(self.driver, self.live_server_url)

    def test_study(self):
        tests.study(self.driver, self.live_server_url)

    def test_bioassay(self):
        tests.bioassay(self.driver, self.live_server_url)

    def test_rob(self):
        tests.rob(self.driver, self.live_server_url)
        pass

    def test_epi(self):
        tests.epi(self.driver, self.live_server_url)

    def test_mgmt(self):
        tests.mgmt(self.driver, self.live_server_url)

    # dynamic apps
    def test_cleanup(self):
        tests.cleanup(self.driver, self.live_server_url)

    def test_summary(self):
        tests.summary(self.driver, self.live_server_url)
