import pytest
from django.urls import reverse

from ..test_utils import check_200, check_403, check_api_json_data, get_client


@pytest.mark.django_db
class TestEpiAssessmentViewSet:
    def test_export(self, rewrite_data_files):
        url = reverse("mgmt:api:assessment-tasks", args=(1,))
        client = get_client(api=True)

        # anon get 403
        check_403(client, url)

        # pm can get valid response
        client = get_client("pm", api=True)
        response = check_200(client, url)
        key = "api-mgmt-tasks-1.json"
        check_api_json_data(response.json(), key, True)
