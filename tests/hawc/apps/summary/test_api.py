import json
import re

import pytest
from django.test.client import Client, RequestFactory
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework.test import APIClient

from hawc.apps.summary import models

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

    def _test_visual_crud_api(self, data, rewrite_data_files: bool, slug: str):
        user_anon = APIClient()
        user_reviewer = APIClient()
        assert user_reviewer.login(username="reviewer@hawcproject.org", password="pw") is True
        user_team = APIClient()
        assert user_team.login(username="team@hawcproject.org", password="pw") is True

        # read visual
        url = models.Visual.objects.get(slug=slug).get_api_detail()
        response = user_anon.get(url)
        assert response.status_code == 200

        resp_data = response.json()
        data_str = json.dumps(resp_data, indent=2, sort_keys=True)
        data_str = re.sub(r"obj_ct=\d+", "obj_ct=9999", data_str)

        key = f"api-visual-{slug}.json"
        check_api_json_data(json.loads(data_str), key, rewrite_data_files)

        # create visual
        url = reverse("summary:api:visual-list")
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
        data = {
            "title": "bioassay-aggregation-2",
            "slug": "bioassay-aggregation-2",
            "visual_type": 0,
            "settings": {},
            "assessment": db_keys.assessment_working,
            "prefilters": {},
            "caption": "<p>caption</p>",
            "published": True,
            "sort_order": "short_citation",
            "endpoints": [],
            "studies": [],
        }
        self._test_visual_crud_api(data, rewrite_data_files, "bioassay-aggregation")

    def test_rob_heatmap(self, rewrite_data_files: bool, db_keys):
        data = {
            "title": "rob-heatmap-2",
            "slug": "rob-heatmap-2",
            "visual_type": 2,
            "settings": json.loads(
                '{"title":"","xAxisLabel":"","yAxisLabel":"","padding_top":20,"cell_size":40,"padding_right":300,"padding_bottom":35,"padding_left":20,"x_field":"study","study_label_field":"short_citation","included_metrics":[14,15],"excluded_score_ids":[],"show_legend":true,"show_na_legend":true,"show_nr_legend":true,"legend_x":231,"legend_y":30}'
            ),
            "assessment": db_keys.assessment_working,
            "prefilters": {},
            "caption": "<p>caption</p>",
            "published": True,
            "sort_order": "short_citation",
            "endpoints": [],
            "studies": [],
        }
        self._test_visual_crud_api(data, rewrite_data_files, "rob-heatmap")

    def test_crossview(self, rewrite_data_files: bool, db_keys):
        data = {
            "title": "crossview-2",
            "slug": "crossview-2",
            "visual_type": 1,
            "settings": json.loads(
                '{"title":"Title","xAxisLabel":"Dose (<add units>)","yAxisLabel":"% change from control (continuous), % incidence (dichotomous)","width":1100,"height":600,"inner_width":940,"inner_height":520,"padding_left":75,"padding_top":45,"dose_isLog":true,"dose_range":"","response_range":"","title_x":0,"title_y":0,"xlabel_x":0,"xlabel_y":0,"ylabel_x":0,"ylabel_y":0,"filters":[{"name":"study","headerName":"Study","allValues":true,"values":null,"columns":1,"x":null,"y":null}],"reflines_dose":[{"value":null,"title":"","style":"base"}],"refranges_dose":[{"lower":null,"upper":null,"title":"","style":"base"}],"reflines_response":[{"value":null,"title":"","style":"base"}],"refranges_response":[{"lower":null,"upper":null,"title":"","style":"base"}],"labels":[{"caption":"","style":"base","max_width":null,"x":null,"y":null}],"colorBase":"#cccccc","colorHover":"#ff4040","colorSelected":"#6495ed","colorFilters":[],"colorFilterLegend":true,"colorFilterLegendLabel":"Color filters","colorFilterLegendX":0,"colorFilterLegendY":0,"endpointFilters":[],"endpointFilterLogic":"and"}'
            ),
            "assessment": db_keys.assessment_working,
            "prefilters": {"animal_group__experiment__study__published": True},
            "caption": "<p>example</p>",
            "published": True,
            "sort_order": "short_citation",
            "endpoints": [],
            "studies": [],
        }
        self._test_visual_crud_api(data, rewrite_data_files, "crossview")

    def test_barchart(self, rewrite_data_files: bool, db_keys):
        data = {
            "title": "barchart-2",
            "slug": "barchart-2",
            "visual_type": 3,
            "settings": json.loads(
                '{"title":"Title","xAxisLabel":"Percent of studies","yAxisLabel":"","plot_width":400,"row_height":30,"padding_top":40,"padding_right":300,"padding_bottom":40,"padding_left":70,"show_values":true,"included_metrics":[14,15],"show_legend":true,"show_na_legend":true,"legend_x":574,"legend_y":10}'
            ),
            "assessment": db_keys.assessment_working,
            "prefilters": {},
            "caption": "<p>caption</p>",
            "published": True,
            "sort_order": "short_citation",
            "endpoints": [],
            "studies": [],
        }
        self._test_visual_crud_api(data, rewrite_data_files, "rob-barchart")

    def test_tagtree(self, rewrite_data_files: bool, db_keys):
        data = {
            "title": "tagtree-2",
            "slug": "tagtree-2",
            "visual_type": 4,
            "settings": json.loads(
                '{"root_node": 11, "required_tags": [], "pruned_tags": [], "hide_empty_tag_nodes": false, "height": 500, "width": 1280, "show_legend": true, "show_counts": true}'
            ),
            "assessment": db_keys.assessment_working,
            "prefilters": {},
            "caption": "<p>caption</p>",
            "published": True,
            "sort_order": "short_citation",
            "endpoints": [],
            "studies": [],
        }
        self._test_visual_crud_api(data, rewrite_data_files, "tagtree")

    def test_embedded_tableau(self, rewrite_data_files: bool, db_keys):
        data = {
            "title": "embedded-tableau-2",
            "slug": "embedded-tableau-2",
            "visual_type": 5,
            "settings": json.loads(
                '{"external_url": "https://public.tableau.com/views/Iris_15675445278420/Iris-Actual", "external_url_hostname": "https://public.tableau.com", "external_url_path": "/views/Iris_15675445278420/Iris-Actual", "external_url_query_args": [":showVizHome=no", ":embed=y"], "filters": []}'
            ),
            "assessment": db_keys.assessment_working,
            "prefilters": {},
            "caption": "<p>iris (flowers)</p>",
            "published": True,
            "sort_order": "short_citation",
            "endpoints": [],
            "studies": [],
        }
        self._test_visual_crud_api(data, rewrite_data_files, "embedded-tableau")

    def test_exploratory_heatmap(self, rewrite_data_files: bool, db_keys):
        data = {
            "title": "exploratory-heatmap-2",
            "slug": "exploratory-heatmap-2",
            "visual_type": 6,
            "settings": json.loads(
                '{"cell_height": 50, "cell_width": 50, "color_range": ["#ffffff", "#cc4700"], "compress_x": true, "compress_y": true, "data_url": "/ani/api/assessment/2/endpoint-heatmap/", "hawc_interactivity": true, "filter_widgets": [{"column": "species", "delimiter": "", "on_click_event": "---", "header": ""}, {"column": "strain", "delimiter": "", "on_click_event": "---", "header": ""}], "padding": {"top": 30, "left": 30, "bottom": 30, "right": 30}, "show_axis_border": true, "show_grid": true, "show_counts": true, "show_tooltip": true, "show_totals": true, "show_null": true, "autosize_cells": true, "autorotate_tick_labels": true, "table_fields": [{"column": "study citation", "delimiter": "", "on_click_event": "study", "header": ""}, {"column": "experiment name", "delimiter": "", "on_click_event": "experiment", "header": ""}, {"column": "animal group name", "delimiter": "", "on_click_event": "animal_group", "header": ""}, {"column": "endpoint name", "delimiter": "", "on_click_event": "endpoint_complete", "header": ""}, {"column": "---", "delimiter": "", "on_click_event": "---", "header": ""}], "title": {"text": "", "x": 0, "y": 0, "rotate": 0}, "x_fields": [{"column": "system", "wrap_text": 0, "delimiter": ""}], "x_label": {"text": "", "x": 0, "y": 0, "rotate": 0}, "x_tick_rotate": 0, "y_fields": [{"column": "study citation", "wrap_text": 0, "delimiter": ""}], "y_label": {"text": "", "x": 0, "y": 0, "rotate": 0}, "y_tick_rotate": -90, "x_axis_bottom": false, "filters": [], "filtersLogic": "and"}'
            ),
            "assessment": db_keys.assessment_working,
            "prefilters": {},
            "caption": "<p>caption</p>",
            "published": True,
            "sort_order": "short_citation",
            "endpoints": [],
            "studies": [],
        }
        self._test_visual_crud_api(data, rewrite_data_files, "exploratory-heatmap")


@pytest.mark.django_db
class TestDataPivot:
    def _test_dp(self, rewrite_data_files: bool, slug: str, fn_key: str, db_keys):
        user_anon = APIClient()
        user_reviewer = APIClient()
        assert user_reviewer.login(username="reviewer@hawcproject.org", password="pw") is True
        user_team = APIClient()
        assert user_team.login(username="team@hawcproject.org", password="pw") is True

        # check DataPivot read
        dp = models.DataPivot.objects.get(slug=slug)
        url = dp.get_api_detail()
        response = user_anon.get(url)
        assert response.status_code == 200

        data = response.json()
        key = f"api-dp-{fn_key}.json"
        check_api_json_data(data, key, rewrite_data_files)

        # check DataPivot data read
        url = dp.get_data_url().replace("tsv", "json")
        response = user_anon.get(url)
        assert response.status_code == 200
        data = response.json()
        key = f"api-dp-data-{fn_key}.json"
        check_api_json_data(data, key, rewrite_data_files)

        # check DataPivotQuery read
        dpq = models.DataPivotQuery.objects.get(slug=slug)
        url = reverse("summary:api:data_pivot_query-detail", args=(dpq.pk,))
        response = user_anon.get(url)
        assert response.status_code == 200

        data = response.json()
        key = f"api-dp_query-{fn_key}.json"
        check_api_json_data(data, key, rewrite_data_files)

        # check DataPivotQuery create
        data["title"] = data["title"] + "-2"
        data["slug"] = data["slug"] + "-2"
        data["assessment"] = db_keys.assessment_working
        url = reverse("summary:api:data_pivot_query-list")
        for user in [user_anon, user_reviewer]:
            response = user.post(url, data, format="json")
            assert response.status_code == 403
        response = user_team.post(url, data, format="json")
        assert response.status_code == 201
        assert response.json()["title"] == data["title"]

        dpq_id = response.json()["id"]
        url = reverse("summary:api:data_pivot_query-detail", args=(dpq_id,))

        # update data pivot
        data["title"] = "updated-title"
        for user in [user_anon, user_reviewer]:
            response = user.patch(url, data, format="json")
            assert response.status_code == 403
        response = user_team.patch(url, data, format="json")
        assert response.status_code == 200
        assert response.json()["title"] == "updated-title"

        # delete data pivot
        for user in [user_anon, user_reviewer]:
            response = user.delete(url, data, format="json")
            assert response.status_code == 403
        response = user_team.delete(url, data, format="json")
        assert response.status_code == 204

    def test_bioassay_endpoint(self, rewrite_data_files: bool, db_keys):
        self._test_dp(
            rewrite_data_files,
            "animal-bioassay-data-pivot-endpoint",
            "animal-bioassay-endpoint",
            db_keys,
        )

    def test_bioassay_endpoint_group(self, rewrite_data_files: bool, db_keys):
        self._test_dp(
            rewrite_data_files,
            "animal-bioassay-data-pivot-endpoint",
            "animal-bioassay-endpoint",
            db_keys,
        )

    def test_epi(self, rewrite_data_files: bool, db_keys):
        self._test_dp(rewrite_data_files, "data-pivot-epi", "epi", db_keys)

    def test_epimeta(self, rewrite_data_files: bool, db_keys):
        self._test_dp(rewrite_data_files, "data-pivot-epimeta", "epimeta", db_keys)

    def test_invitro_endpoint(self, rewrite_data_files: bool, db_keys):
        self._test_dp(
            rewrite_data_files, "data-pivot-invitro-endpoint", "invitro-endpoint", db_keys
        )

    def test_invitro_endpoint_group(self, rewrite_data_files: bool, db_keys):
        self._test_dp(
            rewrite_data_files,
            "data-pivot-invitro-endpoint-group",
            "invitro-endpoint-group",
            db_keys,
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
