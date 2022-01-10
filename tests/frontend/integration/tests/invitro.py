import helium as h

from . import shared


def invitro(driver, root_url):

    shared.login(root_url)

    # /in-vitro/assessment/:id/endpoint-categories/update/
    h.go_to(root_url + "/in-vitro/assessment/2/endpoint-categories/update/")
    h.wait_until(h.Text("Modify in-vitro endpoint categories").exists)

    shared.logout()
