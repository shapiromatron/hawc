import json
import re

import pytest
from django.test.client import Client, RequestFactory
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework.test import APIClient

from hawc.apps.summary import constants, models

from ..test_utils import check_api_json_data


@pytest.mark.django_db
def test_api_visual_heatmap(db_keys):
    client = Client()
    assert client.login(username="team@hawcproject.org", password="pw") is True

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
    assert client.login(username="team@hawcproject.org", password="pw") is True

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

    def _test_visual_crud_api(self, rewrite_data_files: bool, slug: str, assessment_id):
        user_anon = APIClient()
        user_reviewer = APIClient()
        assert user_reviewer.login(username="reviewer@hawcproject.org", password="pw") is True
        user_team = APIClient()
        assert user_team.login(username="team@hawcproject.org", password="pw") is True

        # read visual
        url = models.Visual.objects.get(slug=slug).get_api_detail()
        response = user_anon.get(url)
        assert response.status_code == 200

        data = response.json()
        data_str = json.dumps(data, indent=2, sort_keys=True)
        data_str = re.sub(r"obj_ct=\d+", "obj_ct=9999", data_str)

        key = f"api-visual-{slug}.json"
        check_api_json_data(json.loads(data_str), key, rewrite_data_files)

        visual_types = dict(constants.VisualType.choices)

        # use read data for CUD operations
        data["title"] = data["title"] + "-2"
        data["assessment"] = assessment_id
        data["slug"] = data["slug"] + "-2"
        data["visual_type"] = {
            key for key, value in visual_types.items() if data["visual_type"] in value
        }.pop()
        data["settings"] = json.dumps(data["settings"])
        data["studies"] = []
        data["endpoints"] = []

        # create visual
        for user in [user_anon, user_reviewer]:
            response = user.post(url, data, format="json")
            assert response.status_code == 403
        response = user_team.post(url, data, format="json")
        assert response.status_code == 201
        assert response.json()["title"] == data["title"]

        visual_id = response.json()["id"]
        url = reverse("summary:api:visual-detail", args=(visual_id,))

        # update visual
        data["title"] = "updated-title"
        for user in [user_anon, user_reviewer]:
            response = user.patch(url, data, format="json")
            assert response.status_code == 403
        response = user_team.patch(url, data, format="json")
        assert response.status_code == 200
        assert response.json()["title"] == "updated-title"

        # delete visual
        for user in [user_anon, user_reviewer]:
            response = user.delete(url, data, format="json")
            assert response.status_code == 403
        response = user_team.delete(url, data, format="json")
        assert response.status_code == 204

    def test_bioassay_aggregation(self, rewrite_data_files: bool, db_keys):
        self._test_visual_crud_api(
            rewrite_data_files, "bioassay-aggregation", db_keys.assessment_working
        )

    def test_rob_heatmap(self, rewrite_data_files: bool, db_keys):
        self._test_visual_crud_api(rewrite_data_files, "rob-heatmap", db_keys.assessment_working)

    def test_crossview(self, rewrite_data_files: bool, db_keys):
        self._test_visual_crud_api(rewrite_data_files, "crossview", db_keys.assessment_working)

    def test_barchart(self, rewrite_data_files: bool, db_keys):
        self._test_visual_crud_api(rewrite_data_files, "barchart", db_keys.assessment_working)

    def test_tagtree(self, rewrite_data_files: bool, db_keys):
        self._test_visual_crud_api(rewrite_data_files, "tagtree", db_keys.assessment_working)

    def test_embedded_tableau(self, rewrite_data_files: bool, db_keys):
        self._test_visual_crud_api(
            rewrite_data_files, "embedded-tableau", db_keys.assessment_working
        )

    def test_exploratory_heatmap(self, rewrite_data_files: bool, db_keys):
        self._test_visual_crud_api(
            rewrite_data_files, "exploratory-heatmap", db_keys.assessment_working
        )

    def _test_visual_data_api(self, rewrite_data_files: bool, slug: str):
        client = Client()
        url = models.Visual.objects.get(slug=slug).get_data_url()
        response = client.get(url)
        assert response.status_code == 200

        data = response.json()
        data_str = json.dumps(data, indent=2, sort_keys=True)

        key = f"api-visual-{slug}-data.json"
        check_api_json_data(json.loads(data_str), key, rewrite_data_files)

    def test_rob_heatmap_data(self, rewrite_data_files: bool):
        self._test_visual_data_api(rewrite_data_files, "rob-heatmap")

    def test_barchart_data(self, rewrite_data_files: bool):
        self._test_visual_data_api(rewrite_data_files, "rob-barchart")


@pytest.mark.django_db
class TestDataPivot:
    def _test_dp(self, rewrite_data_files: bool, slug: str, fn_key: str):
        client = Client()

        dp = models.DataPivot.objects.get(slug=slug)
        url = dp.get_api_detail()
        response = client.get(url)
        assert response.status_code == 200

        data = response.json()
        key = f"api-dp-{fn_key}.json"
        check_api_json_data(data, key, rewrite_data_files)

    def _test_dp_data(self, rewrite_data_files: bool, slug: str, fn_key: str):
        client = Client()

        dp = models.DataPivot.objects.get(slug=slug)
        url = dp.get_data_url().replace("tsv", "json")
        response = client.get(url)
        assert response.status_code == 200

        data = response.json()
        key = f"api-dp-data-{fn_key}.json"
        check_api_json_data(data, key, rewrite_data_files)

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
class TestSummaryAssessmentViewSet:
    def test_heatmap_datasets(self, db_keys, rewrite_data_files):
        rev_client = APIClient()
        assert rev_client.login(username="reviewer@hawcproject.org", password="pw") is True
        anon_client = APIClient()

        url = reverse("summary:api:assessment-heatmap-datasets", args=(db_keys.assessment_working,))

        assert anon_client.get(url).status_code == 403

        resp = rev_client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        key = f"api-summary-heatmap-datasets-{db_keys.assessment_working}.json"
        check_api_json_data(data, key, rewrite_data_files)


@pytest.mark.django_db
class TestSummaryTextViewSet:
    def test_current_schema_host(self):
        # undocumented API in django; test to ensure it exists
        factory = RequestFactory()
        request = factory.get("/test")
        assert request._current_scheme_host == "http://testserver"

    def test_permissions(self, db_keys):
        assessment_id = db_keys.assessment_working
        root = models.SummaryText.get_assessment_root_node(assessment_id)

        data = {
            "assessment": assessment_id,
            "title": "lvl_1a",
            "slug": "lvl_1a",
            "text": "text",
            "parent": root.id,
            "sibling": None,
        }
        user_anon = APIClient()
        user_reviewer = APIClient()
        assert user_reviewer.login(username="reviewer@hawcproject.org", password="pw") is True
        user_team = APIClient()
        assert user_team.login(username="team@hawcproject.org", password="pw") is True

        # list
        url = reverse("summary:api:summary-text-list")
        response = user_reviewer.get(url)
        assert response.status_code == 400
        assert "Please provide an `assessment_id`" in response.json()["detail"]
        response = user_reviewer.get(url + f"?assessment_id={assessment_id}")
        assert response.status_code == 200
        assert response.json()[0]["title"] == "assessment-1"

        # creates
        url = reverse("summary:api:summary-text-list")
        for user in [user_anon, user_reviewer]:
            response = user.post(url, data, format="json")
            assert response.status_code == 403
        response = user_team.post(url, data, format="json")
        assert response.status_code == 201
        obj_id = response.json()["id"]

        # updates
        data.update(title="my-title")
        url = reverse("summary:api:summary-text-detail", args=(obj_id,))
        for user in [user_anon, user_reviewer]:
            response = user.patch(url, data, format="json")
            assert response.status_code == 403
        response = user_team.patch(url, data, format="json")
        assert response.status_code == 200
        assert response.json()["title"] == "my-title"

        # deletes
        url = reverse("summary:api:summary-text-detail", args=(obj_id,))
        for user in [user_anon, user_reviewer]:
            response = user.delete(url)
            assert response.status_code == 403
        response = user_team.delete(url)
        assert response.status_code == 204


@pytest.mark.django_db
class TestSummaryTableViewSet:
    def _test_data_file(self, rewrite_data_files: bool, fn_key: str, data):
        data_str = json.dumps(data, indent=2, sort_keys=True)
        data_str = re.sub(r'"content_type_id": \d+', '"content_type_id": 9999', data_str)
        key = f"api-summary-table-{fn_key}-data.json"
        check_api_json_data(json.loads(data_str), key, rewrite_data_files)

    def test_data(self, rewrite_data_files: bool):
        data = {"assessment_id": 1, "table_type": 2, "data_source": "ani", "published_only": False}
        missing_data = {"assessment_id": 1, "table_type": 2, "published_only": False}
        invalid_data = {
            "assessment_id": 1,
            "table_type": 2,
            "data_source": "not a data source",
            "published_only": False,
        }

        base_url = reverse("summary:api:summary-table-data")

        anon_client = APIClient()
        rev_client = APIClient()
        assert rev_client.login(username="reviewer@hawcproject.org", password="pw") is True

        # valid request for authorized user and correct query params
        url = f"{base_url}?{urlencode(data)}"
        resp = rev_client.get(url)
        assert resp.status_code == 200
        self._test_data_file(rewrite_data_files, "set", resp.json())

        # invalid request for unauthorized user
        resp = anon_client.get(url)
        assert resp.status_code == 403

        # invalid request with missing query params
        url = f"{base_url}?{urlencode(missing_data)}"
        resp = rev_client.get(url)
        assert resp.status_code == 400
        assert resp.json() == {"data_source": ["This field is required."]}

        # invalid request with invalid query params
        url = f"{base_url}?{urlencode(invalid_data)}"
        resp = rev_client.get(url)
        assert resp.status_code == 400
        assert resp.json() == {"data_source": ['"not a data source" is not a valid choice.']}

    def test_data_permissions(self, rewrite_data_files: bool):
        # even with a public assessment, must be part of team to view unpublished data
        pub = {"assessment_id": 2, "table_type": 2, "data_source": "ani", "published_only": True}
        unpub = {"assessment_id": 2, "table_type": 2, "data_source": "ani", "published_only": False}
        base_url = reverse("summary:api:summary-table-data")

        # valid request for team member (or reviewer, pm, admin)
        team_client = APIClient()
        assert team_client.login(username="team@hawcproject.org", password="pw") is True
        pub_client = APIClient()
        assert pub_client.login(username="public@hawcproject.org", password="pw") is True

        # team member can view all; non-team-member can only view published
        for client, data, code in [
            (team_client, pub, 200),
            (team_client, unpub, 200),
            (pub_client, pub, 200),
            (pub_client, unpub, 400),
        ]:
            url = f"{base_url}?{urlencode(data)}"
            resp = client.get(url)
            assert resp.status_code == code
            if code == 400:
                assert resp.json() == {
                    "published_only": ["Must be part of team to view unpublished data."]
                }
