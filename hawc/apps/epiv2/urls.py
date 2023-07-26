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
        "designv2/<int:pk>/",
        views.DesignViewSet.as_view(),
        {"action": "read"},
        name="design-detail",
    ),
    path(
        "designv2/<int:pk>/update/",
        views.DesignViewSet.as_view(),
        {"action": "update"},
        name="design-update",
    ),
    # chemical
    path(
        "chemical/<int:pk>/create/",
        views.ChemicalViewSet.as_view(),
        {"action": "create"},
        name="chemical-create",
    ),
    path(
        "chemical/<int:pk>/",
        views.ChemicalViewSet.as_view(),
        {"action": "read"},
        name="chemical-detail",
    ),
    path(
        "chemical/<int:pk>/clone/",
        views.ChemicalViewSet.as_view(),
        {"action": "clone"},
        name="chemical-clone",
    ),
    path(
        "chemical/<int:pk>/update/",
        views.ChemicalViewSet.as_view(),
        {"action": "update"},
        name="chemical-update",
    ),
    path(
        "chemical/<int:pk>/delete/",
        views.ChemicalViewSet.as_view(),
        {"action": "delete"},
        name="chemical-delete",
    ),
    # exposure
    path(
        "exposure/<int:pk>/create/",
        views.ExposureViewSet.as_view(),
        {"action": "create"},
        name="exposure-create",
    ),
    path(
        "exposure/<int:pk>/",
        views.ExposureViewSet.as_view(),
        {"action": "read"},
        name="exposure-detail",
    ),
    path(
        "exposure/<int:pk>/clone/",
        views.ExposureViewSet.as_view(),
        {"action": "clone"},
        name="exposure-clone",
    ),
    path(
        "exposure/<int:pk>/update/",
        views.ExposureViewSet.as_view(),
        {"action": "update"},
        name="exposure-update",
    ),
    path(
        "exposure/<int:pk>/delete/",
        views.ExposureViewSet.as_view(),
        {"action": "delete"},
        name="exposure-delete",
    ),
    # exposure level
    path(
        "exposurelevel/<int:pk>/create/",
        views.ExposureLevelViewSet.as_view(),
        {"action": "create"},
        name="exposurelevel-create",
    ),
    path(
        "exposurelevel/<int:pk>/",
        views.ExposureLevelViewSet.as_view(),
        {"action": "read"},
        name="exposurelevel-detail",
    ),
    path(
        "exposurelevel/<int:pk>/clone/",
        views.ExposureLevelViewSet.as_view(),
        {"action": "clone"},
        name="exposurelevel-clone",
    ),
    path(
        "exposurelevel/<int:pk>/update/",
        views.ExposureLevelViewSet.as_view(),
        {"action": "update"},
        name="exposurelevel-update",
    ),
    path(
        "exposurelevel/<int:pk>/delete/",
        views.ExposureLevelViewSet.as_view(),
        {"action": "delete"},
        name="exposurelevel-delete",
    ),
    # outcome
    path(
        "outcome/<int:pk>/create/",
        views.OutcomeViewSet.as_view(),
        {"action": "create"},
        name="outcome-create",
    ),
    path(
        "outcome/<int:pk>/",
        views.OutcomeViewSet.as_view(),
        {"action": "read"},
        name="outcome-detail",
    ),
    path(
        "outcome/<int:pk>/clone/",
        views.OutcomeViewSet.as_view(),
        {"action": "clone"},
        name="outcome-clone",
    ),
    path(
        "outcome/<int:pk>/update/",
        views.OutcomeViewSet.as_view(),
        {"action": "update"},
        name="outcome-update",
    ),
    path(
        "outcome/<int:pk>/delete/",
        views.OutcomeViewSet.as_view(),
        {"action": "delete"},
        name="outcome-delete",
    ),
    # adjustment factor
    path(
        "adjustmentfactor/<int:pk>/create/",
        views.AdjustmentFactorViewSet.as_view(),
        {"action": "create"},
        name="adjustmentfactor-create",
    ),
    path(
        "adjustmentfactor/<int:pk>/",
        views.AdjustmentFactorViewSet.as_view(),
        {"action": "read"},
        name="adjustmentfactor-detail",
    ),
    path(
        "adjustmentfactor/<int:pk>/clone/",
        views.AdjustmentFactorViewSet.as_view(),
        {"action": "clone"},
        name="adjustmentfactor-clone",
    ),
    path(
        "adjustmentfactor/<int:pk>/update/",
        views.AdjustmentFactorViewSet.as_view(),
        {"action": "update"},
        name="adjustmentfactor-update",
    ),
    path(
        "adjustmentfactor/<int:pk>/delete/",
        views.AdjustmentFactorViewSet.as_view(),
        {"action": "delete"},
        name="adjustmentfactor-delete",
    ),
    # data extraction
    path(
        "dataextraction/<int:pk>/create/",
        views.DataExtractionViewSet.as_view(),
        {"action": "create"},
        name="dataextraction-create",
    ),
    path(
        "dataextraction/<int:pk>/",
        views.DataExtractionViewSet.as_view(),
        {"action": "read"},
        name="dataextraction-detail",
    ),
    path(
        "dataextraction/<int:pk>/clone/",
        views.DataExtractionViewSet.as_view(),
        {"action": "clone"},
        name="dataextraction-clone",
    ),
    path(
        "dataextraction/<int:pk>/update/",
        views.DataExtractionViewSet.as_view(),
        {"action": "update"},
        name="dataextraction-update",
    ),
    path(
        "dataextraction/<int:pk>/delete/",
        views.DataExtractionViewSet.as_view(),
        {"action": "delete"},
        name="dataextraction-delete",
    ),
]
