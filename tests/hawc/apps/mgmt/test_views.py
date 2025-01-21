import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from hawc.apps.mgmt.views import AssessmentAnalytics

from ..test_utils import check_200, check_403, get_client


@pytest.mark.django_db
class TestTaskDashboard:
    def test_view_permissions(self):
        # login required
        c = Client()
        url = reverse("mgmt:user-task-list")
        response = c.get(url, follow=True)
        assertTemplateUsed(response, "registration/login.html")

        # 403 if not part of team
        assert c.login(username="reviewer@hawcproject.org", password="pw") is True
        for url in [
            reverse("mgmt:task-dashboard", args=(1,)),
            reverse("mgmt:task-list", args=(1,)),
        ]:
            response = c.get(url)
            assert response.status_code == 403

    def test_views(self):
        c = Client()
        assert c.login(username="team@hawcproject.org", password="pw") is True

        # my tasks
        url = reverse("mgmt:user-task-list")
        response = c.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "mgmt/user_task_list.html")

        # assessment dashboard
        url = reverse("mgmt:task-dashboard", args=(1,))
        response = c.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "mgmt/assessment_dashboard.html")

        # assessment task list
        url = reverse("mgmt:task-list", args=(1,))
        response = c.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "mgmt/assessment_details.html")

        # task setup list (type, status, trigger)
        url = reverse("mgmt:task-setup-list", args=(1,))
        response = c.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "mgmt/task_setup_list.html")

        # copy task setup
        url = reverse("mgmt:task-setup-copy", args=(1,))
        response = c.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "mgmt/task_setup_copy.html")

    def test_task_htmx(self):
        c = Client(HTTP_HX_REQUEST="true")
        assert c.login(username="team@hawcproject.org", password="pw") is True

        # detail - GET
        url = reverse("mgmt:task-htmx", args=(3, "read"))
        response = c.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "mgmt/fragments/task_detail.html")

        # update - (GET, POST)
        url = reverse("mgmt:task-htmx", args=(3, "update"))
        response = c.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "mgmt/fragments/task_form.html")

        response = c.post(url, data={"task-3-status": 2})
        assert response.status_code == 200
        assertTemplateUsed(response, "mgmt/fragments/task_detail.html")

    def test_task_setup_htmx(self):
        # One test for all task setup htmx because they have a generic parent
        c = Client(HTTP_HX_REQUEST="true")
        assert c.login(username="team@hawcproject.org", password="pw") is True

        # create - (GET, POST)
        url = reverse("mgmt:task-type-htmx", args=(3, "create"))
        response = c.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "mgmt/fragments/type_form.html")

        # read - GET
        url = reverse("mgmt:task-type-htmx", args=(3, "read"))
        response = c.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "mgmt/fragments/type_detail.html")

        # update - (GET, POST)
        url = reverse("mgmt:task-type-htmx", args=(3, "update"))
        response = c.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "mgmt/fragments/type_form.html")

        # delete - (GET, POST)
        url = reverse("mgmt:task-type-htmx", args=(3, "delete"))
        response = c.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "mgmt/fragments/type_form.html")

        # create - (GET, POST)
        url = reverse("mgmt:task-type-htmx", args=(3, "up"))
        response = c.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "mgmt/fragments/setup_table.html")

        # create - (GET, POST)
        url = reverse("mgmt:task-type-htmx", args=(3, "down"))
        response = c.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "mgmt/fragments/setup_table.html")


@pytest.mark.django_db
class TestAnalytics:
    def test_permissions(self):
        url = reverse("mgmt:assessment-analytics", args=(1,))
        client = get_client()
        check_403(client, url)

        client = get_client("pm")
        check_200(client, url)

    def test_actions(self):
        url = reverse("mgmt:assessment-analytics", args=(1,))
        client = get_client("pm")
        templates = {
            "index": "mgmt/analytics.html",
            "time_series": "mgmt/analytics/time_series.html",
            "time_spent": "mgmt/analytics/time_spent.html",
            "overview": "mgmt/analytics/overview.html",
        }
        assert set(AssessmentAnalytics.actions) == set(templates.keys())
        for action, expected_template in templates.items():
            resp = check_200(client, url + f"?action={action}")
            assert resp.templates[0].name == expected_template
