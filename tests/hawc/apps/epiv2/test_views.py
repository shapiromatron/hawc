import pytest
from django.urls import reverse

from ..test_utils import check_200, check_403, get_client


@pytest.mark.django_db
class TestHeatmapStudyDesign:
    def test_permission(self, db_keys):
        url = reverse("epiv2:heatmap-study-design", args=(db_keys.study_working,))
        client = get_client()
        check_403(client, url)

    def test_success(self, db_keys):
        url = reverse("epiv2:heatmap-study-design", args=(db_keys.study_working,))
        client = get_client("pm")
        check_200(client, url)


@pytest.mark.django_db
class TestHeatmapResult:
    def test_permission(self, db_keys):
        url = reverse("epiv2:heatmap-result", args=(db_keys.study_working,))
        client = get_client()
        check_403(client, url)

    def test_success(self, db_keys):
        url = reverse("epiv2:heatmap-result", args=(db_keys.study_working,))
        client = get_client("pm")
        check_200(client, url)


@pytest.mark.django_db
class TestOutcomeView:
    def test_permission(self, db_keys):
        url = reverse("epiv2:outcome", args=(db_keys.study_working,))
        client = get_client()
        check_403(client, url)

    def test_success(self, db_keys):
        url = reverse("epiv2:outcome", args=(db_keys.study_working,))
        client = get_client("pm")
        response = check_200(client, url)
        assert len(response.context["object_list"]) == 3
