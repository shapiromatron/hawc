import pytest
from django.urls import reverse

from hawc.apps.summary import models
from hawc.apps.summary.constants import VisualType

from ..test_utils import check_200, check_404, get_client


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
class TestVisualVisualizationCreate:
    def test_visual_type_200(self):
        # check that each (visual_type, evidence_type) renders successfully
        client = get_client("admin")
        for args in [
            (1, 0),
            (1, 1),
            (1, 2, 0),
            (1, 2, 1),
            (1, 2, 2),
            (1, 3, 0),
            (1, 3, 1),
            (1, 3, 2),
            (1, 4),
            (1, 5),
            (1, 6),
            (1, 7),
            (1, 8),
            (1, 9),
            (1, 10, 0),
            (1, 10, 1),
            (1, 10, 2),
            (1, 10, 4),
            (1, 10, 5),
            (1, 11),
        ]:
            url = reverse("summary:visualization_create", args=args)
            check_200(client, url)

    def test_initial(self):
        client = get_client("pm")
        instance = models.Visual.objects.filter(id=1).first()
        url = (
            reverse(
                "summary:visualization_create", args=(instance.assessment_id, instance.visual_type)
            )
            + f"?initial={instance.id}"
        )
        resp = check_200(client, url)
        assert len(instance.title) > 0
        assert resp.context["form"].initial["title"] == instance.title

    def test_bad_requests(self):
        client = get_client("admin")
        for args in [
            (1, 999),  # bad visual type
            (1, 2, 999),  # bad evidence type
            (1, 2, 3),  # bad evidence type for this visual type
        ]:
            url = reverse("summary:visualization_create", args=args)
            check_404(client, url)


@pytest.mark.django_db
class TestVisualizationUpdateSettings:
    def test_test_404(self):
        client = get_client("admin")

        # works for a datapivot
        obj = models.Visual.objects.filter(visual_type=VisualType.DATA_PIVOT_QUERY).first()
        url = obj.get_dp_update_settings()
        assert client.get(url).status_code == 200

        # but returns 404 for non-data pivot
        obj = models.Visual.objects.filter(visual_type=VisualType.PLOTLY).first()
        url = obj.get_dp_update_settings()
        assert client.get(url).status_code == 404
