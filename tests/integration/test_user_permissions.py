import os

import helium as h
import pytest
import utils.localhost_utils as localhost_utils

SKIP_INTEGRATION = os.environ.get("HAWC_INTEGRATION_TESTS") is None

base_url = "http://localhost:8000"
assessment_url = "/assessment/2/"


@pytest.mark.skipif(SKIP_INTEGRATION, reason="integration test")
def test_user_permissions(chrome_driver):
    # set test to use our session-level driver
    h.set_driver(chrome_driver)

    # go to website
    h.go_to(base_url + assessment_url)
    localhost_utils.remove_debug_menu(chrome_driver)

    h1content = "public final (2001)"
    h1Elem = h.Text(h1content)
    assert h1Elem.exists() is True

    h.go_to(base_url +  assessment_url + "edit/")
    localhost_utils.remove_debug_menu(chrome_driver)

    # From brief googling selenium does not support status code checking, 
    # and I have to scrape the html
    assert h.Text("403. Forbidden").exists() is True
    
    
    h.click("Login")
    assert "/user/login/" in chrome_driver.current_url

    # login to actually hit edit page
    msg = "Please enter a correct email and password."
    assert h.Text(msg).exists() is False
    # TODO: Need an account that actually works in unit testing environment
    # h.write("java_review@epa.gov", into="Email*")
    # h.write("p@ssword123!", into="Password*")
    # h.click("Login")
    # assert "/portal/" in chrome_driver.current_url
    # # untested since can't login

    # # TODO: need to ensure placement in the table again touching the selenium driver underneath
    # assert h.Text(h1Elem).exists() is True

    
    # # since hit login button from edit page should be redirected here
    # assert assessment_url + "edit/" in chrome_driver.current_url

    # # going back to base assessment_url
    # h.go_to(base_url + assessment_url)
    # assert assessment_url in chrome_driver.current_url

    # assert h.Text(h1Elem).exists() is True
    
    # h.click("Update assessment")
    # assert assessment_url + "edit/" in chrome_driver.current_url

