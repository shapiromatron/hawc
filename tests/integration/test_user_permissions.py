import os

import helium as h
import pytest

import utils.localhost_utils as localhost_utils

SKIP_INTEGRATION = os.environ.get("HAWC_INTEGRATION_TESTS") is None


assessment_url = "/assessment/3/"


@pytest.mark.skipif(SKIP_INTEGRATION, reason="integration test")
def test_user_permissions(chrome_driver, integration_base_url):
    base_url = integration_base_url
    # set test to use our session-level driver
    h.set_driver(chrome_driver)

    # go to website
    h.go_to(base_url + assessment_url)
    localhost_utils.remove_debug_menu(chrome_driver)

    assessmentName = "public client (2020)"
    h1Elem = h.Text(assessmentName)
    assert h1Elem.exists() is True

    h.go_to(base_url + assessment_url + "edit/")
    localhost_utils.remove_debug_menu(chrome_driver)

    # From brief googling selenium does not support status code checking,
    # and I have to scrape the html
    assert h.Text("403. Forbidden").exists() is True

    h.go_to(base_url + "/user/login/")
    assert "/user/login/" in chrome_driver.current_url

    # login to actually hit edit page
    msg = "Please enter a correct email and password."
    assert h.Text(msg).exists() is False

    h.write("pm@pm.com", into="Email*")
    h.write("pw", into="Password*")
    h.click("Login")

    assert "/portal/" in chrome_driver.current_url

    # making sure that the assessment name is on the page
    assert h.Text(assessmentName).exists() is True

    h.click(assessmentName)
    localhost_utils.remove_debug_menu(chrome_driver)

    # navigating bootstrap dropdown menu
    h.click("Actions")
    h.click("Update assessment")

    assert assessment_url + "edit/" in chrome_driver.current_url
