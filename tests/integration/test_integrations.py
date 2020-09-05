import os

import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase

from . import tests

SKIP_INTEGRATION = os.environ.get("HAWC_INTEGRATION_TESTS") is None
LIVESERVER_HOST = os.environ.get("LIVESERVER_HOST", None)
LIVESERVER_PORT = os.environ.get("LIVESERVER_PORT", None)
if LIVESERVER_PORT:
    LIVESERVER_PORT = int(LIVESERVER_PORT)


@pytest.mark.skipif(SKIP_INTEGRATION, reason="integration test")
@pytest.mark.usefixtures("set_chrome_driver")
class TestIntegration(StaticLiveServerTestCase, TestCase):
    """
    We use a single class that inherits from both StaticLiveServerTestCase and TestCase
    in order to supersede properties of StaticLiveServerTestCase that cause the database to be
    flushed after every test, while still being able to utilize a live server for HTTP requests.

    Further reading: https://code.djangoproject.com/ticket/23640#comment:3
    """

    host = LIVESERVER_HOST
    port = LIVESERVER_PORT

    def test_login(self):
        tests.login(self.chrome_driver, self.live_server_url)

    def test_rob_browse(self):
        tests.rob_browse(self.chrome_driver, self.live_server_url)

    def test_summary_visual_browse(self):
        tests.summary_visual_browse(self.chrome_driver, self.live_server_url)

    def test_user_permissions(self):
        tests.user_permissions(self.chrome_driver, self.live_server_url)
