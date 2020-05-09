import json
import os
from pathlib import Path

import pytest
from django.test.client import Client
from django.urls import reverse

from hawc.apps.summary import models

DATA_ROOT = Path(__file__).parent / "data"


# rebuild data in this fixture - should ALWAYS be False unless changing
# review diffs after writing
REWRITE_DATA = False


in_ci = os.environ.get("GITHUB_RUN_ID") is not None


@pytest.mark.skipif(not in_ci, reason="only run in CI")
def test_no_data_rewrite():
    # safety check - make sure tests aren't passing b/c we're rewriting expected results...
    if REWRITE_DATA is True:
        raise ValueError("Rewrite data must be set to `False` with commits")


def _rewrite(fn: Path, content):
    fn.write_text(json.dumps(content, indent=2))


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

    def _test_visual_detail_api(self, slug: str):
        client = Client()

        fn = Path(DATA_ROOT / f"api-visual-{slug}.json")
        url = models.Visual.objects.get(slug=slug).get_api_detail()
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()

        if REWRITE_DATA:
            _rewrite(fn, data)
        assert data == json.loads(fn.read_text())

    def test_heatmap(self):
        self._test_visual_detail_api("heatmap")

    def test_crossview(self):
        self._test_visual_detail_api("crossview")

    def test_barchart(self):
        self._test_visual_detail_api("barchart")

    def test_tagtree(self):
        self._test_visual_detail_api("tagtree")

    def test_embedded_tableau(self):
        self._test_visual_detail_api("embedded-tableau")


@pytest.mark.django_db
class TestDataPivot:
    def _test_dp(self, slug: str, fn_key: str):
        client = Client()

        fn = Path(DATA_ROOT / f"api-dp-{fn_key}.json")

        dp = models.DataPivot.objects.get(slug=slug)
        url = dp.get_api_detail()
        response = client.get(url)
        assert response.status_code == 200

        data = response.json()
        if REWRITE_DATA:
            _rewrite(fn, data)
        assert json.loads(fn.read_text()) == data

    def _test_dp_data(self, slug: str, fn_key: str):
        client = Client()

        fn = Path(DATA_ROOT / f"api-dp-data-{fn_key}.json")

        dp = models.DataPivot.objects.get(slug=slug)
        url = dp.get_data_url().replace("tsv", "json")
        response = client.get(url)
        assert response.status_code == 200

        data = response.json()
        if REWRITE_DATA:
            _rewrite(fn, data)
        assert json.loads(fn.read_text()) == data

    def test_bioassay_endpoint(self):
        self._test_dp("animal-bioassay-data-pivot-endpoint", "animal-bioassay-endpoint")
        self._test_dp_data("animal-bioassay-data-pivot-endpoint", "animal-bioassay-endpoint")

    def test_bioassay_endpoint_group(self):
        self._test_dp("animal-bioassay-data-pivot-endpoint", "animal-bioassay-endpoint")
        self._test_dp_data(
            "animal-bioassay-data-pivot-endpoint-group", "animal-bioassay-endpoint-group"
        )

    def test_epimeta(self):
        self._test_dp("data-pivot-epimeta", "epimeta")
        self._test_dp_data("data-pivot-epimeta", "epimeta")
