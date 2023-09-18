import pytest
from django.test.client import Client
from django.urls import reverse

from hawc.apps.summary.models import DataPivotQuery


@pytest.mark.django_db
class TestDataPivotNew:
    def test_initial_settings(self):
        obj = DataPivotQuery.objects.first()
        assert len(obj.settings) > 0

        c = Client()
        assert c.login(username="pm@hawcproject.org", password="pw") is True

        url = reverse("summary:dp_new-query", args=(1, 0))

        # no initial settings or invalid settings
        for args in ["", "?initial=-1", "?initial=-1&reset_row_overrides=1"]:
            resp = c.get(url + args)
            assert resp.status_code == 200 and "form" in resp.context
            assert "settings" not in resp.context["form"].initial

        # initial settings
        for args in [f"?initial={obj.id}", f"?initial={obj.id}&reset_row_overrides=1"]:
            resp = c.get(url + args)
            assert resp.status_code == 200 and "form" in resp.context
            assert "settings" in resp.context["form"].initial
