import pytest
from django.test.client import Client
from django.urls import reverse

from hawc.apps.summary.models import DataPivotQuery
from ..test_utils import check_200, get_client

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

@pytest.mark.django_db
def test_smoke_get():
    client = get_client("admin")
    slug_summary = "Generic-1"
    slug_visual="example-heatmap"
    slug_dp="animal-bioassay-data-pivot-endpoint-group"

    url = reverse("summary:visualization_detail_id", args=(1,))
    assert client.get(url).status_code == 302
    url = reverse("summary:dp_detail_id", args=(1,))
    assert client.get(url).status_code == 302

    urls = [
        # summary tables
        reverse("summary:list", args=(1,)),
        reverse("summary:create", args=(1,)),
        reverse("summary:tables_list", args=(1,)),
        reverse("summary:tables_create_selector", args=(1,)),
        reverse("summary:tables_create", args=(1,1,)),
        reverse("summary:tables_copy", args=(1,)),
        reverse("summary:tables_detail", args=(1,slug_summary,)),
        reverse("summary:tables_update", args=(1,slug_summary)),
        reverse("summary:tables_delete", args=(1,slug_summary)),
        # visualizations
        reverse("summary:visualization_list", args=(1,)),
        reverse("summary:visualization_create_selector", args=(1,)),
        reverse("summary:visualization_create", args=(1,1)),
        reverse("summary:visualization_copy_selector", args=(1,)),
        reverse("summary:visualization_copy", args=(1,1)),
        reverse("summary:visualization_detail", args=(1,slug_visual)),
        reverse("summary:visualization_update", args=(1,slug_visual)),
        reverse("summary:visualization_delete", args=(1,slug_visual)),
        # data-pivot
        reverse("summary:dp_new-prompt", args=(1,)),
        reverse("summary:dp_new-query", args=(1,1)),
        reverse("summary:dp_new-file", args=(1,)),
        reverse("summary:dp_copy_selector", args=(1,)),
        reverse("summary:dp_detail", args=(2,slug_dp)),
        reverse("summary:dp_update", args=(2,slug_dp)),
        reverse("summary:dp_query-update", args=(2,slug_dp)),
        reverse("summary:dp_file-update", args=(2,slug_dp)),
        reverse("summary:dp_delete", args=(2,slug_dp)),
        # help text
        reverse("summary:dataset_interactivity", args=()),
    ]
    for url in urls:
        check_200(client, url)
