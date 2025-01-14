from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import api, views

router = SimpleRouter()
router.register(r"assessment", api.SummaryAssessmentViewSet, basename="assessment")
router.register(r"visual", api.VisualViewSet, basename="visual")
router.register(r"summary-table", api.SummaryTableViewSet, basename="summary-table")

app_name = "summary"
urlpatterns = [
    # API
    path("api/", include((router.urls, "api"))),
    # SUMMARY TABLES
    path("assessment/<int:pk>/tables/", views.SummaryTableList.as_view(), name="tables_list"),
    path(
        "assessment/<int:pk>/tables/create/",
        views.SummaryTableCreateSelector.as_view(),
        name="tables_create_selector",
    ),
    path(
        "assessment/<int:pk>/tables/<int:table_type>/create/",
        views.SummaryTableCreate.as_view(),
        name="tables_create",
    ),
    path(
        "assessment/<int:pk>/tables/copy/",
        views.SummaryTableCopy.as_view(),
        name="tables_copy",
    ),
    path(
        "assessment/<int:pk>/tables/<slug:slug>/",
        views.SummaryTableDetail.as_view(),
        name="tables_detail",
    ),
    path(
        "assessment/<int:pk>/tables/<slug:slug>/update/",
        views.SummaryTableUpdate.as_view(),
        name="tables_update",
    ),
    path(
        "assessment/<int:pk>/tables/<slug:slug>/delete/",
        views.SummaryTableDelete.as_view(),
        name="tables_delete",
    ),
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
        "assessment/<int:pk>/visuals/<int:visual_type>/create/<int:study_type>/",
        views.VisualizationCreate.as_view(),
        name="visualization_create",
    ),
    path(
        "assessment/<int:pk>/visuals/copy/",
        views.VisualizationCopySelector.as_view(),
        name="visualization_copy_selector",
    ),
    path(
        "assessment/<int:pk>/visuals/<int:visual_type>/copy/",
        views.VisualizationCopy.as_view(),
        name="visualization_copy",
    ),
    path(
        "assessment/<int:pk>/type/<int:visual_type>/<int:study_type>/data/",
        views.VisualizationCreateTester.as_view(),
        name="visualization_create_tester",
    ),
    path(
        "visual/<int:pk>/",
        views.VisualizationByIdDetail.as_view(),
        name="visualization_detail_id",
    ),
    path(
        "visual/assessment/<int:pk>/<slug:slug>/",
        views.VisualizationDetail.as_view(),
        name="visualization_detail",
    ),
    path(
        "visual/assessment/<int:pk>/<slug:slug>/update/",
        views.VisualizationUpdate.as_view(),
        name="visualization_update",
    ),
    path(
        "visual/assessment/<int:pk>/<slug:slug>/update-settings/",
        views.VisualizationUpdateSettings.as_view(),
        name="visualization_update_settings",
    ),
    path(
        "visual/assessment/<int:pk>/<slug:slug>/delete/",
        views.VisualizationDelete.as_view(),
        name="visualization_delete",
    ),
    # HELP TEXT
    path(
        "dataset-interactivity/",
        views.DatasetInteractivity.as_view(),
        name="dataset_interactivity",
    ),
]
