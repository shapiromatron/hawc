import os

import helium as h
import pytest

SKIP_INTEGRATION = os.environ.get("HAWC_INTEGRATION_TESTS") is None


assessment_url = "/assessment/3/"


@pytest.mark.skipif(SKIP_INTEGRATION, reason="integration test")
def test_user_permissions(chrome_driver, live_server):
    # set test to use our session-level driver
    h.set_driver(chrome_driver)

    # go to website
    h.go_to(live_server.url + assessment_url)

    assessmentName = "public client (2020)"
    h1Elem = h.Text(assessmentName)
    assert h1Elem.exists() is True

    h.go_to(live_server.url + assessment_url + "edit/")

    # From brief googling selenium does not support status code checking,
    # and I have to scrape the html
    assert h.Text("403. Forbidden").exists() is True

    h.go_to(live_server.url + "/user/login/")
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

    # navigating bootstrap dropdown menu
    h.click("Actions")
    h.click("Update assessment")

    assert assessment_url + "edit/" in chrome_driver.current_url
