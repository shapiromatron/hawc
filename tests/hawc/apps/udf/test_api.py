import pytest
from django.urls import reverse

from hawc.apps.udf.models import ModelUDFContent, TagUDFContent

from ..test_utils import check_200, check_403, check_api_json_data, get_client


@pytest.mark.django_db
class TestUdfAssessmentViewSet:
    def test_model_export(self, rewrite_data_files):
        url = reverse("udf:api:assessment-export-model-udfs", args=(4,))
        client = get_client(api=True)

        # anon get 403
        check_403(client, url)

        # pm can get valid response
        client = get_client("team", api=True)
        response = check_200(client, url)
        key = "api-udf-model-export-1.json"
        data = response.json()
        assert len(data) == 1
        check_api_json_data(data, key, rewrite_data_files)

    def test_model_export_filter(self):
        url = reverse("udf:api:assessment-export-model-udfs", args=(4,))
        client = get_client("team", api=True)

        # check content_type filter
        url += "?content_type=study.study"
        response = check_200(client, url)
        assert len(response.json()) == 1

        url = url.replace("study.study", "foo.foo")
        response = check_200(client, url)
        assert len(response.json()) == 0

    def test_tag_export(self, rewrite_data_files):
        url = reverse("udf:api:assessment-export-tag-udfs", args=(1,))
        client = get_client(api=True)

        # anon get 403
        check_403(client, url)

        # pm can get valid response
        client = get_client("team", api=True)
        response = check_200(client, url)
        key = "api-udf-tag-export-1.json"
        data = response.json()
        assert len(data) == 1
        check_api_json_data(data, key, rewrite_data_files)

    def test_tag_export_filter(self):
        url = reverse("udf:api:assessment-export-tag-udfs", args=(1,))
        client = get_client("team", api=True)

        # check content_type filter
        url += "?tag=2"
        response = check_200(client, url)
        assert len(response.json()) == 1

        url = url.replace("?tag=2", "?tag=234")
        response = check_200(client, url)
        assert len(response.json()) == 0

    def test_tag_binding_export(self, rewrite_data_files):
        url = reverse("udf:api:assessment-export-tag-bindings", args=(1,))
        client = get_client("team", api=True)

        response = check_200(client, url)
        key = "api-udf-tag-binding-export-1.json"
        data = response.json()
        assert len(data) == 1
        check_api_json_data(data, key, rewrite_data_files)

    def test_model_binding_export(self, rewrite_data_files):
        url = reverse("udf:api:assessment-export-model-bindings", args=(4,))
        client = get_client("team", api=True)

        response = check_200(client, url)
        key = "api-udf-model-binding-export-1.json"
        data = response.json()
        assert len(data) == 1
        check_api_json_data(data, key, rewrite_data_files)

    def test_tag_content_create(self, rewrite_data_files):
        url = reverse("udf:api:assessment-tag-content", args=(1,))
        client = get_client("team", api=True)
        data = {
            "tag_binding": 1,
            "reference": 1,
            "content": {"field1": "updated data", "field2": 123},
        }
        resp = client.post(url, data, format="json")
        import pdb

        pdb.set_trace()
        tag_content = TagUDFContent.objects.get(reference=1, tag_binding=1)
        assert tag_content.content == data["content"]
