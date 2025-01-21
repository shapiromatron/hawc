import time

import pytest
from django.urls import reverse

from hawc.apps.eco import models

from ..test_utils import check_200, check_403, check_timespent, get_client, get_timespent


@pytest.mark.django_db
def test_get_200():
    client = get_client("pm")
    urls = [
        reverse("eco:term_list"),
    ]
    for url in urls:
        check_200(client, url)


@pytest.mark.django_db
class TestHeatmapStudyDesign:
    def test_permission(self, db_keys):
        url = reverse("eco:heatmap_study_design", args=(db_keys.study_working,))
        client = get_client()
        check_403(client, url)

    def test_success(self, db_keys):
        url = reverse("eco:heatmap_study_design", args=(db_keys.study_working,))
        client = get_client("pm")
        check_200(client, url)


@pytest.mark.django_db
class TestHeatmapResult:
    def test_permission(self, db_keys):
        url = reverse("eco:heatmap_results", args=(db_keys.study_working,))
        client = get_client()
        check_403(client, url)

    def test_success(self, db_keys):
        url = reverse("eco:heatmap_results", args=(db_keys.study_working,))
        client = get_client("pm")
        check_200(client, url)


@pytest.mark.django_db
class TestResultView:
    def test_permission(self, db_keys):
        url = reverse("eco:result_list", args=(db_keys.study_working,))
        client = get_client()
        check_403(client, url)

    def test_success(self, db_keys):
        url = reverse("eco:result_list", args=(db_keys.study_working,))
        client = get_client("pm")
        response = check_200(client, url)
        assert len(response.context["object_list"]) == 1


@pytest.mark.django_db
class TestNestedTermList:
    def test_query(self):
        url = reverse("eco:term_list")
        client = get_client("pm")

        response = check_200(client, url + "?name__contains=zzz")
        assert len(response.context["object_list"]) == 0

        response = check_200(client, url + "?name__contains=term")
        assert len(response.context["object_list"]) == 1


@pytest.mark.django_db
class TestTimeSpentEditing:
    def _valid_design(self):
        return {
            "name": "example eco design",
            "design": "1",
            "study_setting": "6",
            "countries": ["2"],
            "states": [],
            "ecoregions": ["110"],
            "habitats": ["12"],
            "habitats_as_reported": "habitat here",
            "climates": ["103"],
            "climates_as_reported": "climate here",
        }

    def _valid_cause(self):
        return {
            "cause-new-name": "Total N",
            "cause-new-term": 1,
            "cause-new-level": "0.054-12.4",
            "cause-new-level_units": "mg/L",
            "cause-new-duration": "NA",
        }

    # check that TestTimeSpentEditing is captured for this app
    def test_design(self, db_keys):
        client = get_client("team")
        latest = get_timespent()
        htmx_headers = {"hx-request": "true"}

        # check DesignCreate
        assert not isinstance(latest.content_object, models.Design)
        url = reverse("eco:design_create", args=(db_keys.study_working,))
        client.get(url)
        time.sleep(0.05)
        resp = client.post(url, data=self._valid_design(), follow=True)
        assert resp.status_code == 200
        design = resp.context["object"]
        latest = check_timespent(design)
        seconds = latest.seconds

        # check DesignViewSet update
        url = reverse("eco:design-htmx", args=(design.id, "update"))
        resp = client.get(url, headers=htmx_headers)
        time.sleep(0.05)
        resp = client.post(url, data=self._valid_design(), headers=htmx_headers)
        assert resp.status_code == 200
        latest = check_timespent(design)
        assert latest.seconds > seconds

        # check DesignChildViewSet create
        url = reverse("eco:cause-htmx", args=(design.id, "create"))
        client.get(url)
        time.sleep(0.05)
        resp = client.post(url, data=self._valid_cause(), headers=htmx_headers)
        assert resp.status_code == 200
        cause = resp.context["object"]
        latest = check_timespent(cause)
        seconds = latest.seconds

        # check DesignChildViewSet update
        url = reverse("eco:cause-htmx", args=(cause.id, "update"))
        resp = client.get(url, headers=htmx_headers)
        time.sleep(0.05)
        data = {v.replace("new", str(cause.id)): k for v, k in self._valid_cause().items()}
        resp = client.post(url, data=data, headers=htmx_headers)
        assert resp.status_code == 200
        latest = check_timespent(cause)
        assert latest.seconds > seconds
