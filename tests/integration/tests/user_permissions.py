import helium as h

assessment_url = "/assessment/3/"


def user_permissions(chrome_driver, live_server_url):
    h.set_driver(chrome_driver)

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
    assert "/user/login/" in chrome_driver.current_url
    msg = "Please enter a correct email and password."
    assert h.Text(msg).exists() is False
    h.write("pm@pm.com", into="Email*")
    h.write("pw", into="Password*")
    h.click("Login")
    assert "/portal/" in chrome_driver.current_url

    # now, try to go to edit url
    h.go_to(edit_url)
    assert edit_url == chrome_driver.current_url

    # logout; cleanup test
    h.click("Your HAWC")
    h.click("Logout")
