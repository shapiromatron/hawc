import time

import pytest
from django.urls import reverse

from hawc.apps.epiv2 import models

from ..test_utils import check_200, check_403, check_timespent, get_client, get_timespent


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


@pytest.mark.django_db
class TestTimeSpentEditing:
    def _valid_design(self):
        return {
            "study_design": "CC",
            "source": "GP",
            "age_description": "10-15 yrs",
            "sex": "B",
            "race": "Not specified but likely primarily Asian",
            "summary": "test epidemiology study design",
            "study_name": "Genetic and Biomarkers study for Childhood Asthma",
            "region": "northern Taiwan",
            "years": "2009-2010",
            "participant_n": 456,
            "age_profile": "AD",
        }

    def _valid_chemical(self):
        return {"chemical-new-name": "example"}

    # check that TestTimeSpentEditing is captured for this app
    def test_design(self, db_keys):
        client = get_client("team")
        latest = get_timespent()
        htmx_headers = {"hx-request": "true"}

        # check DesignCreate
        assert not isinstance(latest.content_object, models.Design)
        url = reverse("epiv2:design_create", args=(db_keys.study_working,))
        client.get(url)
        time.sleep(0.05)
        resp = client.post(url, data=self._valid_design(), follow=True)
        assert resp.status_code == 200
        design = resp.context["object"]
        latest = check_timespent(design)
        seconds = latest.seconds

        # check DesignViewSet update
        url = reverse("epiv2:design-htmx", args=(design.id, "update"))
        resp = client.get(url, headers=htmx_headers)
        time.sleep(0.05)
        resp = client.post(url, data=self._valid_design(), headers=htmx_headers)
        assert resp.status_code == 200
        latest = check_timespent(design)
        assert latest.seconds > seconds

        # check DesignChildViewSet create
        url = reverse("epiv2:chemical-htmx", args=(design.id, "create"))
        client.get(url)
        time.sleep(0.05)
        resp = client.post(url, data=self._valid_chemical(), headers=htmx_headers)
        assert resp.status_code == 200
        chemical = resp.context["object"]
        latest = check_timespent(chemical)
        seconds = latest.seconds

        # check DesignChildViewSet update
        url = reverse("epiv2:chemical-htmx", args=(chemical.id, "update"))
        resp = client.get(url, headers=htmx_headers)
        time.sleep(0.05)
        data = {v.replace("new", str(chemical.id)): k for v, k in self._valid_chemical().items()}
        resp = client.post(url, data=data, headers=htmx_headers)
        assert resp.status_code == 200
        latest = check_timespent(chemical)
        assert latest.seconds > seconds
