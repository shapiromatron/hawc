from django.urls import include, re_path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"assessment", api.SummaryAssessmentViewset, basename="assessment")
router.register(r"visual", api.VisualViewset, basename="visual")
router.register(r"data_pivot", api.DataPivotViewset, basename="data_pivot")

app_name = "summary"
urlpatterns = [
    # API
    re_path(r"^api/", include((router.urls, "api"))),
    # SUMMARY-TEXT
    re_path(r"^assessment/(?P<pk>\d+)/summaries/$", views.SummaryTextList.as_view(), name="list",),
    re_path(
        r"^assessment/(?P<pk>\d+)/summaries/modify/$",
        views.SummaryTextCreate.as_view(),
        name="create",
    ),
    re_path(r"^(?P<pk>\d+)/update/$", views.SummaryTextUpdate.as_view(), name="update"),
    re_path(r"^(?P<pk>\d+)/delete/$", views.SummaryTextDelete.as_view(), name="delete"),
    re_path(
        r"^assessment/(?P<pk>\d+)/summaries/json/$", views.SummaryTextJSON.as_view(), name="json",
    ),
    # VISUALIZATIONS
    re_path(
        r"^assessment/(?P<pk>\d+)/visuals/$",
        views.VisualizationList.as_view(),
        name="visualization_list",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/visuals/create/$",
        views.VisualizationCreateSelector.as_view(),
        name="visualization_create_selector",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/visuals/(?P<visual_type>\d+)/create/$",
        views.VisualizationCreate.as_view(),
        name="visualization_create",
    ),
    re_path(
        r"^assessment/(?P<pk>\d+)/type/(?P<visual_type>\d+)/data/$",
        views.VisualizationCreateTester.as_view(),
        name="visualization_create_tester",
    ),
    re_path(
        r"^visual/(?P<pk>\d+)/$", views.VisualizationDetail.as_view(), name="visualization_detail",
    ),
    re_path(
        r"^visual/(?P<pk>\d+)/update/$",
        views.VisualizationUpdate.as_view(),
        name="visualization_update",
    ),
    re_path(
        r"^visual/(?P<pk>\d+)/delete/$",
        views.VisualizationDelete.as_view(),
        name="visualization_delete",
    ),
    # DATA-PIVOT
    re_path(
        r"^data-pivot/assessment/(?P<pk>\d+)/new/$",
        views.DataPivotNewPrompt.as_view(),
        name="dp_new-prompt",
    ),
    re_path(
        r"^data-pivot/assessment/(?P<pk>\d+)/new/query/$",
        views.DataPivotQueryNew.as_view(),
        name="dp_new-query",
    ),
    re_path(
        r"^data-pivot/assessment/(?P<pk>\d+)/new/file/$",
        views.DataPivotFileNew.as_view(),
        name="dp_new-file",
    ),
    re_path(
        r"^data-pivot/assessment/(?P<pk>\d+)/new/copy-as-new-selector/$",
        views.DataPivotCopyAsNewSelector.as_view(),
        name="dp_copy_selector",
    ),
    re_path(
        r"^data-pivot/(?P<pk>\d+)/$", views.DataPivotByIdDetail.as_view(), name="dp_detail_id",
    ),
    re_path(
        r"^data-pivot/assessment/(?P<pk>\d+)/(?P<slug>[\w-]+)/$",
        views.DataPivotDetail.as_view(),
        name="dp_detail",
    ),
    re_path(
        r"^data-pivot/assessment/(?P<pk>\d+)/(?P<slug>[\w-]+)/update/$",
        views.DataPivotUpdateSettings.as_view(),
        name="dp_update",
    ),
    re_path(
        r"^data-pivot/assessment/(?P<pk>\d+)/(?P<slug>[\w-]+)/query-update/$",
        views.DataPivotUpdateQuery.as_view(),
        name="dp_query-update",
    ),
    re_path(
        r"^data-pivot/assessment/(?P<pk>\d+)/(?P<slug>[\w-]+)/file-update/$",
        views.DataPivotUpdateFile.as_view(),
        name="dp_file-update",
    ),
    re_path(
        r"^data-pivot/assessment/(?P<pk>\d+)/(?P<slug>[\w-]+)/delete/$",
        views.DataPivotDelete.as_view(),
        name="dp_delete",
    ),
]
