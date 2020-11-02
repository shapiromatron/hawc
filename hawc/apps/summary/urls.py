from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api, views

router = DefaultRouter()
router.register(r"assessment", api.SummaryAssessmentViewset, basename="assessment")
router.register(r"visual", api.VisualViewset, basename="visual")
router.register(r"data_pivot", api.DataPivotViewset, basename="data_pivot")

app_name = "summary"
urlpatterns = [
    # API
    path("api/", include((router.urls, "api"))),
    # SUMMARY-TEXT
    path("assessment/<int:pk>/summaries/", views.SummaryTextList.as_view(), name="list",),
    path(
        "assessment/<int:pk>/summaries/modify/", views.SummaryTextCreate.as_view(), name="create",
    ),
    path("<int:pk>/update/", views.SummaryTextUpdate.as_view(), name="update"),
    path("<int:pk>/delete/", views.SummaryTextDelete.as_view(), name="delete"),
    path("assessment/<int:pk>/summaries/json/", views.SummaryTextJSON.as_view(), name="json",),
    # VISUALIZATIONS
    path(
        "assessment/<int:pk>/visuals/",
        views.VisualizationList.as_view(),
        name="visualization_list",
    ),
    path(
        "assessment/<int:pk>/visuals/create/",
        views.VisualizationCreateSelector.as_view(),
        name="visualization_create_selector",
    ),
    path(
        "assessment/<int:pk>/visuals/<int:visual_type>/create/",
        views.VisualizationCreate.as_view(),
        name="visualization_create",
    ),
    path(
        "assessment/<int:pk>/type/<int:visual_type>/data/",
        views.VisualizationCreateTester.as_view(),
        name="visualization_create_tester",
    ),
    path("visual/<int:pk>/", views.VisualizationDetail.as_view(), name="visualization_detail",),
    path(
        "visual/<int:pk>/update/", views.VisualizationUpdate.as_view(), name="visualization_update",
    ),
    path(
        "visual/<int:pk>/delete/", views.VisualizationDelete.as_view(), name="visualization_delete",
    ),
    # DATA-PIVOT
    path(
        "data-pivot/assessment/<int:pk>/new/",
        views.DataPivotNewPrompt.as_view(),
        name="dp_new-prompt",
    ),
    path(
        "data-pivot/assessment/<int:pk>/new/query/",
        views.DataPivotQueryNew.as_view(),
        name="dp_new-query",
    ),
    path(
        "data-pivot/assessment/<int:pk>/new/file/",
        views.DataPivotFileNew.as_view(),
        name="dp_new-file",
    ),
    path(
        "data-pivot/assessment/<int:pk>/new/copy-as-new-selector/",
        views.DataPivotCopyAsNewSelector.as_view(),
        name="dp_copy_selector",
    ),
    path("data-pivot/<int:pk>/", views.DataPivotByIdDetail.as_view(), name="dp_detail_id",),
    path(
        "data-pivot/assessment/<int:pk>/<slug:slug>/",
        views.DataPivotDetail.as_view(),
        name="dp_detail",
    ),
    path(
        "data-pivot/assessment/<int:pk>/<slug:slug>/update/",
        views.DataPivotUpdateSettings.as_view(),
        name="dp_update",
    ),
    path(
        "data-pivot/assessment/<int:pk>/<slug:slug>/query-update/",
        views.DataPivotUpdateQuery.as_view(),
        name="dp_query-update",
    ),
    path(
        "data-pivot/assessment/<int:pk>/<slug:slug>/file-update/",
        views.DataPivotUpdateFile.as_view(),
        name="dp_file-update",
    ),
    path(
        "data-pivot/assessment/<int:pk>/<slug:slug>/delete/",
        views.DataPivotDelete.as_view(),
        name="dp_delete",
    ),
]
