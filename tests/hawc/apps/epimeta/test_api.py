import pytest
from django.urls import reverse, reverse_lazy

from ..test_utils import check_api_json_data, get_client


@pytest.mark.django_db
class TestAssessmentViewSet:
    def test_permissions(self, db_keys):
        rev_client = get_client(role="reviewer", api=True)
        anon_client = get_client(api=True)

        urls = [
            reverse("meta:api:assessment-export", args=(db_keys.assessment_working,)),
        ]
        for url in urls:
            assert anon_client.get(url).status_code == 403
            assert rev_client.get(url).status_code == 200

    def test_full_export(self, rewrite_data_files: bool, db_keys):
        fn = "api-epimeta-assessment-export.json"
        url = (
            reverse("meta:api:assessment-export", args=(db_keys.assessment_final,)) + "?format=json"
        )

        client = get_client(api=True)
        resp = client.get(url)
        assert resp.status_code == 200
        check_api_json_data(resp.json(), fn, rewrite_data_files)


@pytest.mark.parametrize(
    "url",
    [
        reverse_lazy("meta:api:protocol-detail", args=(1,)),
        reverse_lazy("meta:api:result-detail", args=(1,)),
    ],
)
@pytest.mark.django_db
def test_valid_serializers(url, db_keys):
    client = get_client("pm", api=True)
    resp = client.get(url)
    assert resp.status_code == 200
    assert len(resp.json()) > 0
