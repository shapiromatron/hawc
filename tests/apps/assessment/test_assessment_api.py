import time

import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.vcr
class TestCasrnView:
    def test_happy_path(self):
        casrn = "7732-18-5"
        url = reverse("assessment:casrn_detail", args=(casrn,))

        assert url == "/assessment/casrn/7732-18-5/"

        # first time, acknowledge request
        client = APIClient()
        resp = client.get(url)
        data = resp.json()
        assert data == {"status": "requesting"}

        # wait until success
        waited_for = 0
        while waited_for < 10:
            resp = client.get(url)
            data = resp.json()
            if data["status"] == "success":
                break

            time.sleep(1)
            waited_for += 1

        if waited_for >= 10:
            raise RuntimeError("Failed to return successful request")

        assert data["content"]["common_name"] == "Water"

    def test_bad_casrn(self):
        casrn = "1-1-1"
        url = reverse("assessment:casrn_detail", args=(casrn,))

        assert url == "/assessment/casrn/1-1-1/"

        # first time, acknowledge request
        client = APIClient()
        resp = client.get(url)
        data = resp.json()
        assert data == {"status": "requesting"}

        # wait until failure
        waited_for = 0
        while waited_for < 10:
            resp = client.get(url)
            data = resp.json()
            if data["status"] == "failed":
                break

            time.sleep(1)
            waited_for += 1

        if waited_for >= 10:
            raise RuntimeError("Failed to return incorrect request")

        assert data == {"status": "failed", "content": {}}
