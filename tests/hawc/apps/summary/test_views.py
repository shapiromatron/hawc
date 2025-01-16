import pytest
from django.urls import reverse

from hawc.apps.summary import constants, models

from ..test_utils import check_200, get_client


@pytest.mark.django_db
def test_get_redirect():
    client = get_client("admin")
    urls = [
        reverse("summary:visualization_detail_id", args=(2,)),
        reverse("summary:legacy-dp-redirect", args=(2, "legacy-dp-slug")),
    ]
    for url in urls:
        assert client.get(url).status_code == 302


@pytest.mark.django_db
def test_get_200():
    client = get_client("admin")
    main = 1
    secondary = 2
    slug_summary = "Generic-1"
    slug_visual = "example-heatmap"
    slug_dp = "animal-bioassay-data-pivot-endpoint-group"
    table_type = 1
    visual_type = 1

    urls = [
        # summary tables
        reverse("summary:tables_list", args=(main,)),
        reverse("summary:tables_create_selector", args=(main,)),
        reverse("summary:tables_create", args=(main, table_type)),
        reverse("summary:tables_copy", args=(main,)),
        reverse("summary:tables_detail", args=(main, slug_summary)),
        reverse("summary:tables_update", args=(main, slug_summary)),
        reverse("summary:tables_delete", args=(main, slug_summary)),
        # visualizations
        reverse("summary:visualization_list", args=(main,)),
        reverse("summary:visualization_create_selector", args=(main,)),
        reverse("summary:visualization_create", args=(main, visual_type)),
        reverse("summary:visualization_copy_selector", args=(main,)),
        reverse("summary:visualization_copy", args=(main, visual_type)),
        reverse("summary:visualization_detail", args=(main, slug_visual)),
        reverse("summary:visualization_update", args=(main, slug_visual)),
        reverse("summary:visualization_delete", args=(main, slug_visual)),
        # data-pivot
        reverse("summary:visualization_detail", args=(secondary, slug_dp)),
        reverse("summary:visualization_update", args=(secondary, slug_dp)),
        reverse("summary:visualization_update_settings", args=(secondary, slug_dp)),
        # help text
        reverse("summary:dataset_interactivity"),
    ]
    for url in urls:
        check_200(client, url)


@pytest.mark.django_db
class TestVisualizationUpdateSettings:
    def test_test_404(self):
        client = get_client("admin")

        # works for a datapivot
        obj = models.Visual.objects.filter(
            visual_type=constants.VisualType.DATA_PIVOT_QUERY
        ).first()
        url = obj.get_dp_update_settings()
        assert client.get(url).status_code == 200

        # but returns 404 for non-data pivot
        obj = models.Visual.objects.filter(visual_type=constants.VisualType.PLOTLY).first()
        url = obj.get_dp_update_settings()
        assert client.get(url).status_code == 404
