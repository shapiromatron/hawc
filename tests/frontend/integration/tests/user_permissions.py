import helium as h

from . import shared

assessment_url = "/assessment/3/"


def user_permissions(driver, root_url):
    """
    Basic permissions checks, ensure that some basic assessment-level checks are valid
    - unauthenticated users can view detail pages but not update pages
    - authenticated users with project permissions can view update pages
    """
    detail_url = root_url + assessment_url
    edit_url = root_url + assessment_url + "update/"

    # check w/o authentication we can view the public url
    h.go_to(detail_url)
    assessmentName = "Chemical Y (2020)"
    h1Elem = h.Text(assessmentName)
    assert h1Elem.exists() is True

    # check we cannot go to edit url
    h.go_to(edit_url)
    assert h.Text("403. Forbidden").exists() is True

    # login
    shared.login(root_url)
    assert "/portal/" in driver.current_url

    # now, try to go to edit url
    h.go_to(edit_url)
    assert edit_url == driver.current_url

    shared.logout()
