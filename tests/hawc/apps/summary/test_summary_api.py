import json
from pathlib import Path

import pytest
from django.test.client import Client
from django.urls import reverse
from rest_framework.test import APIClient

from hawc.apps.summary import models

DATA_ROOT = Path(__file__).parents[3] / "data/api"


@pytest.mark.django_db
def test_api_visual_heatmap(db_keys):
    client = Client()
    assert client.login(username="team@team.com", password="pw") is True

    url = reverse("summary:api:visual-detail", args=(db_keys.visual_heatmap,))
    response = client.get(url)
    assert response.status_code == 200

    json = response.json()
    assert json["title"] == "example heatmap"
    assert json["settings"] == {
        "title": "",
        "xAxisLabel": "",
        "yAxisLabel": "",
        "padding_top": 20,
        "cell_size": 40,
        "padding_right": 400,
        "padding_bottom": 35,
        "padding_left": 20,
        "x_field": "study",
        "study_label_field": "short_citation",
        "included_metrics": [1, 2],
        "excluded_score_ids": [],
        "show_legend": True,
        "show_na_legend": True,
        "show_nr_legend": True,
        "legend_x": 239,
        "legend_y": 17,
    }


@pytest.mark.django_db
def test_api_visual_barchart(db_keys):
    client = Client()
    assert client.login(username="team@team.com", password="pw") is True

    # test rob barchart request returns successfully
    url = reverse("summary:api:visual-detail", args=(db_keys.visual_barchart,))
    response = client.get(url)
    assert response.status_code == 200

    json = response.json()
    assert json["title"] == "example barchart"
    assert json["settings"] == {
        "title": "Title",
        "xAxisLabel": "Percent of studies",
        "yAxisLabel": "",
        "plot_width": 400,
        "row_height": 30,
        "padding_top": 40,
        "padding_right": 400,
        "padding_bottom": 40,
        "padding_left": 70,
        "show_values": True,
        "included_metrics": [1, 2],
        "show_legend": True,
        "show_na_legend": True,
        "legend_x": 640,
        "legend_y": 10,
    }


@pytest.mark.django_db
class TestVisual:
    """
    Make sure our API gives expected results for all visual types
    """

    def _test_visual_detail_api(self, rewrite_data_files: bool, slug: str):
        client = Client()

        fn = Path(DATA_ROOT / f"api-visual-{slug}.json")
        url = models.Visual.objects.get(slug=slug).get_api_detail()
        response = client.get(url)

        assert response.status_code == 200

        data = response.json()

        if rewrite_data_files:
            fn.write_text(json.dumps(data, indent=2))

        assert data == json.loads(fn.read_text())

    def test_heatmap(self, rewrite_data_files: bool):
        self._test_visual_detail_api(rewrite_data_files, "heatmap")

    def test_crossview(self, rewrite_data_files: bool):
        self._test_visual_detail_api(rewrite_data_files, "crossview")

    def test_barchart(self, rewrite_data_files: bool):
        self._test_visual_detail_api(rewrite_data_files, "barchart")

    def test_tagtree(self, rewrite_data_files: bool):
        self._test_visual_detail_api(rewrite_data_files, "tagtree")

    def test_embedded_tableau(self, rewrite_data_files: bool):
        self._test_visual_detail_api(rewrite_data_files, "embedded-tableau")


@pytest.mark.django_db
class TestDataPivot:
    def _test_dp(self, rewrite_data_files: bool, slug: str, fn_key: str):
        client = Client()

        fn = Path(DATA_ROOT / f"api-dp-{fn_key}.json")

        dp = models.DataPivot.objects.get(slug=slug)
        url = dp.get_api_detail()
        response = client.get(url)
        assert response.status_code == 200

        data = response.json()

        if rewrite_data_files:
            fn.write_text(json.dumps(data, indent=2))

        assert json.loads(fn.read_text()) == data

    def _test_dp_data(self, rewrite_data_files: bool, slug: str, fn_key: str):
        client = Client()

        fn = Path(DATA_ROOT / f"api-dp-data-{fn_key}.json")

        dp = models.DataPivot.objects.get(slug=slug)
        url = dp.get_data_url().replace("tsv", "json")
        response = client.get(url)
        assert response.status_code == 200

        data = response.json()

        if rewrite_data_files:
            fn.write_text(json.dumps(data, indent=2))

        assert json.loads(fn.read_text()) == data

    def test_bioassay_endpoint(self, rewrite_data_files: bool):
        self._test_dp(
            rewrite_data_files, "animal-bioassay-data-pivot-endpoint", "animal-bioassay-endpoint"
        )
        self._test_dp_data(
            rewrite_data_files, "animal-bioassay-data-pivot-endpoint", "animal-bioassay-endpoint"
        )

    def test_bioassay_endpoint_group(self, rewrite_data_files: bool):
        self._test_dp(
            rewrite_data_files, "animal-bioassay-data-pivot-endpoint", "animal-bioassay-endpoint"
        )
        self._test_dp_data(
            rewrite_data_files,
            "animal-bioassay-data-pivot-endpoint-group",
            "animal-bioassay-endpoint-group",
        )

    def test_epi(self, rewrite_data_files: bool):
        self._test_dp(rewrite_data_files, "data-pivot-epi", "epi")
        self._test_dp_data(rewrite_data_files, "data-pivot-epi", "epi")

    def test_epimeta(self, rewrite_data_files: bool):
        self._test_dp(rewrite_data_files, "data-pivot-epimeta", "epimeta")
        self._test_dp_data(rewrite_data_files, "data-pivot-epimeta", "epimeta")

    def test_invitro_endpoint(self, rewrite_data_files: bool):
        self._test_dp(rewrite_data_files, "data-pivot-invitro-endpoint", "invitro-endpoint")
        self._test_dp_data(rewrite_data_files, "data-pivot-invitro-endpoint", "invitro-endpoint")

    def test_invitro_endpoint_group(self, rewrite_data_files: bool):
        self._test_dp(
            rewrite_data_files, "data-pivot-invitro-endpoint-group", "invitro-endpoint-group"
        )
        self._test_dp_data(
            rewrite_data_files, "data-pivot-invitro-endpoint-group", "invitro-endpoint-group"
        )


@pytest.mark.django_db
class TestSummaryAssessmentViewset:
    def test_heatmap_datasets(self, db_keys):
        rev_client = APIClient()
        assert rev_client.login(username="rev@rev.com", password="pw") is True
        anon_client = APIClient()

        urls = [
            reverse("summary:api:assessment-heatmap-datasets", args=(db_keys.assessment_working,)),
        ]
        for url in urls:
            assert anon_client.get(url).status_code == 403
            resp = rev_client.get(url)
            assert resp.status_code == 200
            assert resp.json() == {
                "datasets": [
                    {
                        "type": "Literature",
                        "name": "Literature summary",
                        "url": "/lit/api/assessment/1/tag-heatmap/",
                    },
                    {
                        "type": "Bioassay",
                        "name": "Bioassay study design",
                        "url": "/ani/api/assessment/1/study-heatmap/",
                    },
                    {
                        "type": "Bioassay",
                        "name": "Bioassay study design (including unpublished HAWC data)",
                        "url": "/ani/api/assessment/1/study-heatmap/?unpublished=true",
                    },
                    {
                        "type": "Bioassay",
                        "name": "Bioassay endpoint summary",
                        "url": "/ani/api/assessment/1/endpoint-heatmap/",
                    },
                    {
                        "type": "Bioassay",
                        "name": "Bioassay endpoint summary (including unpublished HAWC data)",
                        "url": "/ani/api/assessment/1/endpoint-heatmap/?unpublished=true",
                    },
                    {
                        "type": "Bioassay",
                        "name": "Bioassay endpoint with doses",
                        "url": "/ani/api/assessment/1/endpoint-doses-heatmap/",
                    },
                    {
                        "type": "Bioassay",
                        "name": "Bioassay endpoint with doses (including unpublished HAWC data)",
                        "url": "/ani/api/assessment/1/endpoint-doses-heatmap/?unpublished=true",
                    },
                    {
                        "type": "Epi",
                        "name": "Epidemiology study design",
                        "url": "/epi/api/assessment/1/study-heatmap/",
                    },
                    {
                        "type": "Epi",
                        "name": "Epidemiology study design (including unpublished HAWC data)",
                        "url": "/epi/api/assessment/1/study-heatmap/?unpublished=true",
                    },
                    {
                        "type": "Epi",
                        "name": "Epidemiology result summary",
                        "url": "/epi/api/assessment/1/result-heatmap/",
                    },
                    {
                        "type": "Epi",
                        "name": "Epidemiology result summary (including unpublished HAWC data)",
                        "url": "/epi/api/assessment/1/result-heatmap/?unpublished=true",
                    },
                    {
                        "type": "Dataset",
                        "name": "Dataset: iris flowers",
                        "url": "/assessment/api/dataset/1/data/",
                    },
                    {
                        "type": "Dataset",
                        "name": "Dataset: iris flowers unpublished",
                        "url": "/assessment/api/dataset/3/data/",
                    },
                ]
            }
