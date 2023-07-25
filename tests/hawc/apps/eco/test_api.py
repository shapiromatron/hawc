import pytest
from django.urls import reverse

from ..test_utils import check_200, check_403, check_api_json_data, get_client


@pytest.mark.django_db
class TestAssessmentViewSet:
    def test_assessment(self, rewrite_data_files):
        url = reverse("eco:api:assessment-export", args=(1,))
        client = get_client(api=True)

        # check permissions; must be authenticated
        check_403(client, url)

        # check successful status code
        client = get_client("pm", api=True)
        response = check_200(client, url + "?unpublished=true")
        key = "api-eco-export-1.json"
        check_api_json_data(response.json(), key, rewrite_data_files)

    def test_study(self, rewrite_data_files):
        url = reverse("eco:api:assessment-study-export", args=(1,))
        client = get_client(api=True)

        # check permissions; must be authenticated
        check_403(client, url)

        # check successful status code
        client = get_client("pm", api=True)
        response = check_200(client, url + "?unpublished=true")
        key = "api-eco-study-export-1.json"
        check_api_json_data(response.json(), key, rewrite_data_files)


@pytest.mark.django_db
class TestTermViewSet:
    def test_nested(self, rewrite_data_files):
        url = reverse("eco:api:terms-nested")
        client = get_client(api=True)

        # check permissions; must be authenticated
        check_403(client, url)

        # check successful status code
        client = get_client("pm", api=True)
        response = check_200(client, url + "?unpublished=true")
        key = "api-eco-term-export.json"
        check_api_json_data(response.json(), key, rewrite_data_files)
