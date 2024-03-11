from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import api, views

router = SimpleRouter()
router.register("assessment", api.EpiAssessmentViewSet, basename="assessment")
router.register("design", api.DesignViewSet, basename="design")
router.register("metadata", api.MetadataViewSet, basename="metadata")
router.register("chemical", api.ChemicalViewSet, basename="chemical")
router.register("exposure", api.ExposureViewSet, basename="exposure")
router.register("exposure-level", api.ExposureLevelViewSet, basename="exposure-level")
router.register("outcome", api.OutcomeViewSet, basename="outcome")
router.register("adjustment-factor", api.AdjustmentFactorViewSet, basename="adjustment-factor")
router.register("data-extraction", api.DataExtractionViewSet, basename="data-extraction")
router.register("design-cleanup", api.DesignCleanupViewSet, basename="design-cleanup")
router.register("chemical-cleanup", api.ChemicalCleanupViewSet, basename="chemical-cleanup")
router.register("exposure-cleanup", api.ExposureCleanupViewSet, basename="exposure-cleanup")
router.register(
    "exposure-level-cleanup", api.ExposureLevelCleanupViewSet, basename="exposure-level-cleanup"
)
router.register("outcome-cleanup", api.OutcomeCleanupViewSet, basename="outcome-cleanup")
router.register(
    "adjustment-factor-cleanup",
    api.AdjustmentFactorCleanupViewSet,
    basename="adjustment-factor-cleanup",
)
router.register(
    "data-extraction-cleanup", api.DataExtractionCleanupViewSet, basename="data-extraction-cleanup"
)

app_name = "epiv2"
urlpatterns = [
    path("api/", include((router.urls, "api"))),
    # Heatmap views
    path(
        "assessment/<int:pk>/heatmap-study-design/",
        views.HeatmapStudyDesign.as_view(),
        name="heatmap-study-design",
    ),
    path(
        "assessment/<int:pk>/heatmap-result/",
        views.HeatmapResult.as_view(),
        name="heatmap-result",
    ),
    # List views
    path(
        "assessment/<int:pk>/outcomes/",
        views.OutcomeView.as_view(),
        name="outcome",
    ),
    # CRUD
    path(
        "study/<int:pk>/design/create/",
        views.DesignCreate.as_view(),
        name="design_create",
    ),
    path(
        "design/<int:pk>/update/",
        views.DesignUpdate.as_view(),
        name="design_update",
    ),
    path(
        "design/<int:pk>/",
        views.DesignDetail.as_view(),
        name="design_detail",
    ),
    path(
        "design/<int:pk>/delete/",
        views.DesignDelete.as_view(),
        name="design_delete",
    ),
    # design htmx viewset
    path(
        "designv2/<int:pk>/<slug:action>/",
        views.DesignViewSet.as_view(),
        name="design-htmx",
    ),
    # chemical
    path(
        "chemical/<int:pk>/<slug:action>/",
        views.ChemicalViewSet.as_view(),
        name="chemical-htmx",
    ),
    # exposure
    path(
        "exposure/<int:pk>/<slug:action>/",
        views.ExposureViewSet.as_view(),
        name="exposure-htmx",
    ),
    # exposure level
    path(
        "exposurelevel/<int:pk>/<slug:action>/",
        views.ExposureLevelViewSet.as_view(),
        name="exposurelevel-htmx",
    ),
    # outcome
    path(
        "outcome/<int:pk>/<slug:action>/",
        views.OutcomeViewSet.as_view(),
        name="outcome-htmx",
    ),
    # adjustment factor
    path(
        "adjustmentfactor/<int:pk>/<slug:action>/",
        views.AdjustmentFactorViewSet.as_view(),
        name="adjustmentfactor-htmx",
    ),
    # data extraction
    path(
        "dataextraction/<int:pk>/<slug:action>/",
        views.DataExtractionViewSet.as_view(),
        name="dataextraction-htmx",
    ),
]
