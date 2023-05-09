import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed


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
            reverse("mgmt:user-assessment-task-list", args=(1,)),
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

        # assessment user task list
        url = reverse("mgmt:user-assessment-task-list", args=(1,))
        response = c.get(url)
        assertTemplateUsed(response, "mgmt/user_assessment_task_list.html")
        assert response.status_code == 200

    def test_htmx(self):
        c = Client(HTTP_HX_REQUEST="true")
        assert c.login(username="team@hawcproject.org", password="pw") is True

        # detail - GET
        url = reverse("mgmt:task-detail", args=(3,))
        response = c.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "mgmt/fragments/task_cell.html")

        # update - (GET, POST)
        url = reverse("mgmt:task-update", args=(3,))
        response = c.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "mgmt/fragments/task_form.html")

        response = c.post(url, data=dict(status=20))
        assert response.status_code == 200
        assertTemplateUsed(response, "mgmt/fragments/task_cell.html")
