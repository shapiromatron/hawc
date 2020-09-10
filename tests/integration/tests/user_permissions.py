import helium as h

assessment_url = "/assessment/3/"


def user_permissions(driver, live_server_url):
    """
    Basic permissions checks, ensure that some basic assessment-level checks are valid
    - unauthenticated users can view detail pages but not update pages
    - authenticated users with project permissions can view update pages
    """
    h.set_driver(driver)

    detail_url = live_server_url + assessment_url
    edit_url = live_server_url + assessment_url + "edit/"

    # check w/o authentication we can view the public url
    h.go_to(detail_url)
    assessmentName = "public client (2020)"
    h1Elem = h.Text(assessmentName)
    assert h1Elem.exists() is True

    # check we cannot go to edit url
    h.go_to(edit_url)
    assert h.Text("403. Forbidden").exists() is True

    # login
    h.go_to(live_server_url + "/user/login/")
    assert "/user/login/" in driver.current_url
    msg = "Please enter a correct email and password."
    assert h.Text(msg).exists() is False
    h.write("pm@pm.com", into="Email*")
    h.write("pw", into="Password*")
    h.click("Login")
    assert "/portal/" in driver.current_url

    # now, try to go to edit url
    h.go_to(edit_url)
    assert edit_url == driver.current_url

    # logout; cleanup test
    h.click("Your HAWC")
    h.click("Logout")
